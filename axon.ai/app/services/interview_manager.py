import uuid
from typing import Optional, Any
from pydantic import BaseModel, Field

from app.services.difficulty import DifficultyEngine, DifficultyState
from app.services.vector_store import query_chunks
from app.services.llm_service import (
    generate_grounded_question,
    evaluate_answer,
    synthesize_interview_performance
)
from app.models.interview import (
    TurnEvaluation,
    SessionHistoryItem,
    InterviewStateResponse,
    SynthesisResponse
)


class SessionRecord(BaseModel):
    session_id: str
    candidate_id: str
    student_name: str
    mode: str = "practice"  # 'practice' or 'graded'
    status: str = "in_progress"  # 'in_progress', 'completed'
    role_track: str = "Software Engineer"
    target_skill: Optional[str] = None
    max_questions: int = 25
    current_turn: int = 1
    current_question: str
    difficulty_state: DifficultyState
    history: list[SessionHistoryItem] = Field(default_factory=list)
    synthesis_result: Optional[dict[str, Any]] = None


class InterviewSessionManager:
    """
    Manages interview session lifecycle, state transitions, context retrieval,
    turn evaluations, and synthesis.
    """
    def __init__(self):
        self._sessions: dict[str, SessionRecord] = {}

    def _retrieve_resume_context(self, candidate_id: str, query: str = "skills projects experience") -> str:
        """Retrieves top resume chunks from ChromaDB."""
        try:
            chunks = query_chunks(candidate_id, query_text=query, top_k=3)
            if chunks:
                return "\n\n".join([f"[{c['section']}]\n{c['chunk_text']}" for c in chunks])
        except Exception as e:
            print(f"[InterviewManager] Note: ChromaDB query returned: {e}")
        
        # Fallback context if no resume uploaded yet
        return "Candidate has general software engineering, algorithm, and backend development experience."

    def start_session(
        self,
        candidate_id: str,
        student_name: str = "Candidate",
        mode: str = "practice",
        role_track: str = "Software Engineer",
        target_skill: Optional[str] = None,
        max_questions: int = 25
    ) -> tuple[str, str, str]:
        """
        Initializes an interview session and generates the first grounded question.
        Returns: (session_id, first_question, topic)
        """
        session_id = str(uuid.uuid4())
        initial_difficulty = DifficultyEngine.create_initial_state(starting_level=2)
        
        # Build initial grounded context
        resume_context = self._retrieve_resume_context(candidate_id, query=target_skill or role_track)
        
        first_question = generate_grounded_question(
            resume_context=resume_context,
            role_topic=role_track,
            difficulty_level=initial_difficulty.current_level,
            turn_index=1,
            target_skill=target_skill,
            previous_questions=[]
        )

        record = SessionRecord(
            session_id=session_id,
            candidate_id=candidate_id,
            student_name=student_name,
            mode=mode.lower(),
            status="in_progress",
            role_track=role_track,
            target_skill=target_skill,
            max_questions=max_questions,
            current_turn=1,
            current_question=first_question,
            difficulty_state=initial_difficulty,
            history=[]
        )

        self._sessions[session_id] = record
        return session_id, first_question, role_track

    def submit_answer(
        self,
        session_id: str,
        answer: str
    ) -> tuple[TurnEvaluation, Optional[str], bool]:
        """
        Processes candidate's answer for the current question:
        1. Evaluates answer (decoupled).
        2. Updates difficulty state deterministically.
        3. Appends to session history.
        4. Generates next question if turns remain, or completes session.
        Returns: (TurnEvaluation, next_question_or_None, is_completed)
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session '{session_id}' not found.")

        session = self._sessions[session_id]
        if session.status != "in_progress":
            raise ValueError(f"Session '{session_id}' is already {session.status}.")

        current_q = session.current_question
        current_lvl = session.difficulty_state.current_level

        # Step 1: Decoupled answer evaluation
        raw_eval = evaluate_answer(
            question=current_q,
            answer=answer,
            difficulty_level=current_lvl
        )

        evaluation = TurnEvaluation(
            score=float(raw_eval.get("score", 5.0)),
            technical_accuracy=raw_eval.get("technical_accuracy", "N/A"),
            areas_for_improvement=raw_eval.get("areas_for_improvement", "N/A"),
            feedback=raw_eval.get("feedback", "N/A"),
            difficulty_level=current_lvl
        )

        # Step 2: Append turn to history
        session.history.append(SessionHistoryItem(
            turn=session.current_turn,
            question=current_q,
            answer=answer,
            evaluation=evaluation,
            difficulty_level=current_lvl
        ))

        # Step 3: Update difficulty deterministically
        updated_diff_state, transition_msg = DifficultyEngine.evaluate_transition(
            session.difficulty_state,
            evaluation.score
        )
        session.difficulty_state = updated_diff_state

        # Step 4: Check if reached max questions
        if session.current_turn >= session.max_questions:
            session.status = "completed"
            return evaluation, None, True

        # Step 5: Advance turn and generate next grounded question
        session.current_turn += 1
        prev_questions = [h.question for h in session.history]
        resume_context = self._retrieve_resume_context(
            session.candidate_id,
            query=f"{session.role_track} {session.target_skill or ''}"
        )

        next_question = generate_grounded_question(
            resume_context=resume_context,
            role_topic=session.role_track,
            difficulty_level=session.difficulty_state.current_level,
            turn_index=session.current_turn,
            target_skill=session.target_skill,
            previous_questions=prev_questions
        )

        session.current_question = next_question
        return evaluation, next_question, False

    def conclude_session(self, session_id: str) -> SynthesisResponse:
        """
        Synthesizes complete session results, radar scores, and learning roadmap.
        In 'graded' mode: evaluates task auto-close and score eligibility.
        In 'practice' mode: delivers student roadmap without writing to official score records.
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session '{session_id}' not found.")

        session = self._sessions[session_id]
        session.status = "completed"

        if not session.synthesis_result:
            qa_logs = [
                {
                    "turn": h.turn,
                    "question": h.question,
                    "answer": h.answer,
                    "score": h.evaluation.score if h.evaluation else 0.0,
                    "technical_accuracy": h.evaluation.technical_accuracy if h.evaluation else "",
                    "difficulty_level": h.difficulty_level
                }
                for h in session.history
            ]

            synthesis = synthesize_interview_performance(qa_logs, mode=session.mode)
            session.synthesis_result = synthesis
        else:
            synthesis = session.synthesis_result

        # Check task auto-closure loop
        tasks_closed = []
        if session.mode == "graded" and session.target_skill:
            domain_scores = synthesis.get("domain_scores", {})
            # Look for score matching or containing target skill
            skill_matched = False
            for s_name, s_val in domain_scores.items():
                if session.target_skill.lower() in s_name.lower():
                    if float(s_val) >= 7.0:
                        tasks_closed.append(f"Auto-closed task: {session.target_skill} (Score: {s_val}/10)")
                    skill_matched = True
                    break
            if not skill_matched and float(synthesis.get("overall_score", 0.0)) >= 7.0:
                tasks_closed.append(f"Auto-closed task: {session.target_skill} (Overall Performance: {synthesis.get('overall_score')}/10)")

        return SynthesisResponse(
            session_id=session.session_id,
            mode=session.mode,
            overall_score=float(synthesis.get("overall_score", 6.0)),
            technical_depth=float(synthesis.get("technical_depth", 6.0)),
            logical_reasoning=float(synthesis.get("logical_reasoning", 6.0)),
            communication_clarity=float(synthesis.get("communication_clarity", 6.0)),
            domain_scores={k: float(v) for k, v in synthesis.get("domain_scores", {}).items()},
            strengths=synthesis.get("strengths", []),
            weaknesses=synthesis.get("weaknesses", []),
            roadmap=synthesis.get("roadmap", []),
            tasks_auto_closed=tasks_closed
        )

    def get_session_state(self, session_id: str) -> InterviewStateResponse:
        """Returns the full state of a session."""
        if session_id not in self._sessions:
            raise KeyError(f"Session '{session_id}' not found.")

        session = self._sessions[session_id]
        return InterviewStateResponse(
            session_id=session.session_id,
            candidate_id=session.candidate_id,
            student_name=session.student_name,
            mode=session.mode,
            status=session.status,
            current_turn=session.current_turn,
            max_questions=session.max_questions,
            difficulty_level=session.difficulty_state.current_level,
            history=session.history
        )


# Global singleton instance
interview_manager = InterviewSessionManager()
