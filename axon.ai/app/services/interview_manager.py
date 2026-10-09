import uuid
from typing import Optional, Any
from pydantic import BaseModel, Field

from app.services.difficulty import DifficultyEngine, DifficultyState
from app.services.vector_store import query_chunks
from app.services.keyword_engine import question_selector
from app.services.evaluator import answer_evaluator
from app.services.synthesizer import session_synthesizer
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
    current_question_id: str = ""
    current_model_answer: str = ""
    current_keywords: list[str] = Field(default_factory=list)
    current_stage: str = "easy"
    resume_context: str = ""
    asked_question_ids: list[str] = Field(default_factory=list)
    chain_history: list[str] = Field(default_factory=list)
    difficulty_state: DifficultyState
    history: list[SessionHistoryItem] = Field(default_factory=list)
    synthesis_result: Optional[SynthesisResponse] = None


class InterviewSessionManager:
    """
    Manages interview session lifecycle using the Offline Keyword-Chain Recommendation Engine.
    - Turns 1 to 5: Stage 1 = Easy (Levels 1-2)
    - Turns 6 to 12: Stage 2 = Medium (Level 3)
    - Turns 13+: Stage 3 = Hard (Levels 4-5)
    - Next question is chained from keywords extracted from the candidate's previous answer.
    - Decoupled answer evaluation using TF-IDF cosine similarity and keyword coverage.
    - Statistical session synthesis producing multi-dimensional radar scores and actionable roadmaps.
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
            print(f"[InterviewManager] Note: Vector retrieval: {e}")
        
        return "General software engineering, machine learning, data structures, and backend development experience."

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
        Initializes an interview session and selects the first Easy question.
        Returns: (session_id, first_question, topic)
        """
        session_id = str(uuid.uuid4())
        initial_difficulty = DifficultyEngine.create_initial_state(starting_level=2)
        
        # Build initial resume context
        resume_context = self._retrieve_resume_context(candidate_id, query=target_skill or role_track)
        
        # Select initial Easy question (Turn 1)
        first_q_data = question_selector.select_first_question(
            topic=role_track,
            resume_context=resume_context
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
            current_question=first_q_data["question_text"],
            current_question_id=first_q_data["id"],
            current_model_answer=first_q_data.get("model_answer", ""),
            current_keywords=first_q_data.get("keywords", []),
            current_stage="easy",
            resume_context=resume_context,
            asked_question_ids=[first_q_data["id"]],
            chain_history=[first_q_data.get("chain_reason", "Opening question")],
            difficulty_state=initial_difficulty,
            history=[]
        )

        self._sessions[session_id] = record
        return session_id, record.current_question, role_track

    def submit_answer(
        self,
        session_id: str,
        answer: str
    ) -> tuple[TurnEvaluation, Optional[str], bool]:
        """
        Processes candidate's answer for the current turn:
        1. Evaluates answer against current model answer and expected keywords.
        2. Updates difficulty state deterministically.
        3. Appends turn to session history.
        4. Selects next question chained from keywords in the candidate's answer adhering to:
           - Turns 1-5: Easy
           - Turns 6-12: Medium
           - Turns 13+: Hard
        Returns: (TurnEvaluation, next_question_or_None, is_completed)
        """
        if session_id not in self._sessions:
            raise KeyError(f"Session '{session_id}' not found.")

        session = self._sessions[session_id]
        if session.status != "in_progress":
            raise ValueError(f"Session '{session_id}' is already {session.status}.")

        current_q = session.current_question
        current_lvl = session.difficulty_state.current_level

        # Step 1: Algorithmic answer evaluation
        evaluation = answer_evaluator.evaluate(
            question=current_q,
            student_answer=answer,
            model_answer=session.current_model_answer,
            expected_keywords=session.current_keywords,
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

        # Step 5: Advance turn and select next chained question
        session.current_turn += 1
        asked_ids = session.asked_question_ids

        next_q_data = question_selector.select_next_question(
            previous_answer=answer,
            current_turn=session.current_turn,
            asked_ids=asked_ids,
            resume_context=session.resume_context
        )

        session.current_question = next_q_data["question_text"]
        session.current_question_id = next_q_data["id"]
        session.asked_question_ids.append(next_q_data["id"])
        session.current_model_answer = next_q_data.get("model_answer", "")
        session.current_keywords = next_q_data.get("keywords", [])
        session.current_stage = next_q_data.get("stage", "medium")
        session.chain_history.append(next_q_data.get("chain_reason", ""))

        return evaluation, session.current_question, False

    def conclude_session(self, session_id: str) -> SynthesisResponse:
        """
        Synthesizes complete session results, radar scores, and learning roadmap.
        In 'graded' mode: evaluates task auto-close and score eligibility.
        In 'practice' mode: delivers student roadmap without official score mutation.
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
                    "evaluation": h.evaluation,
                    "difficulty_level": h.difficulty_level,
                    "topic": session.role_track
                }
                for h in session.history
            ]

            synthesis = session_synthesizer.synthesize(
                session_id=session.session_id,
                mode=session.mode,
                qa_history=qa_logs,
                target_skill=session.target_skill
            )
            session.synthesis_result = synthesis
        else:
            synthesis = session.synthesis_result

        return synthesis

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
