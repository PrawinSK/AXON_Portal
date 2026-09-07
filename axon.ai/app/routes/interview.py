from fastapi import APIRouter, HTTPException, Path, Depends
from app.models.interview import (
    StartInterviewRequest,
    StartInterviewResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    InterviewStateResponse,
    SynthesisResponse
)
from app.services.interview_manager import interview_manager
from app.services.key_pool import key_pool
from app.services.auth_service import require_role

router = APIRouter(
    prefix="/interview",
    tags=["Adaptive Interview"]
)


@router.post("/start", response_model=StartInterviewResponse)
def start_interview(payload: StartInterviewRequest):
    """
    Initializes a new interview session for a student candidate.
    - Grounds the opening question in the candidate's resume and role track.
    - Calibrates initial difficulty state (Level 2).
    - Sets session mode ('practice' or 'graded').
    """
    try:
        session_id, first_q, topic = interview_manager.start_session(
            candidate_id=payload.candidate_id,
            student_name=payload.student_name,
            mode=payload.mode,
            role_track=payload.role_track,
            target_skill=payload.target_skill,
            max_questions=payload.max_questions
        )
        return StartInterviewResponse(
            session_id=session_id,
            mode=payload.mode,
            status="in_progress",
            current_turn=1,
            max_questions=payload.max_questions,
            first_question=first_q,
            based_on_topic=topic
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start interview: {str(e)}")


@router.post("/{session_id}/answer", response_model=SubmitAnswerResponse)
def submit_answer(
    payload: SubmitAnswerRequest,
    session_id: str = Path(..., description="Unique interview session ID")
):
    """
    Processes a candidate's answer for the current question turn:
    - Decoupled answer evaluation with numerical score (1.0 - 10.0).
    - Deterministic difficulty adaptation (promotion/demotion).
    - Returns evaluation feedback and the next grounded question.
    """
    try:
        eval_result, next_q, is_completed = interview_manager.submit_answer(
            session_id=session_id,
            answer=payload.answer
        )
        session_state = interview_manager.get_session_state(session_id)
        
        return SubmitAnswerResponse(
            session_id=session_id,
            turn_completed=len(session_state.history),
            max_questions=session_state.max_questions,
            is_completed=is_completed,
            evaluation=eval_result,
            next_question=next_q
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error evaluating answer: {str(e)}")


@router.get("/{session_id}/state", response_model=InterviewStateResponse)
def get_interview_state(
    session_id: str = Path(..., description="Unique interview session ID")
):
    """
    Returns the complete state of an interview session, including current turn,
    hidden difficulty level, and full Q&A turn history.
    """
    try:
        return interview_manager.get_session_state(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")


@router.post("/{session_id}/conclude", response_model=SynthesisResponse)
def conclude_interview(
    session_id: str = Path(..., description="Unique interview session ID")
):
    """
    Concludes the interview and executes end-of-session synthesis:
    - Generates multi-dimensional radar scores (Technical Depth, Logic, Communication).
    - Generates week-by-week learning roadmap.
    - Evaluates task auto-close if in 'graded' mode.
    """
    try:
        return interview_manager.conclude_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")


@router.get("/pool/status")
def get_key_pool_status(current_user: dict = Depends(require_role(["hod"]))):
    """
    Diagnostics endpoint reporting the health, total capacity, and active keys
    in the 50-key Google Gemini rotation pool. Strictly restricted to HOD.
    """
    return key_pool.get_pool_status()
