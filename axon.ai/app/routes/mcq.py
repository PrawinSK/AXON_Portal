from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Path
from pydantic import BaseModel

from app.services.auth_service import require_role, get_current_user
from app.services.mcq_service import mcq_service
from app.services.mcq_parser import mcq_parser

router = APIRouter(prefix="/mcq", tags=["MCQ Assessment"])


class SubmitAnswersRequest(BaseModel):
    answers: Dict[str, str]


class UpdateQuestionRequest(BaseModel):
    question_text: str
    options: list[str]
    correct_answer: str
    explanation: str = ""
    topic: str = "General IT / Computer Science"
    is_approved: bool = True


class ApprovalToggleRequest(BaseModel):
    is_approved: bool


@router.post("/upload")
async def upload_mcq_bank(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_role(["staff", "hod"]))
):
    """
    Allows Staff or HOD to upload an MCQ question bank via Excel (.xlsx, .xls, .csv) or PDF.
    Extracts questions, choices, answers (or resolves missing answers via external source).
    """
    content = await mcq_parser.validate_and_read_file(file)
    parsed_questions = mcq_parser.parse_mcqs(file.filename or "questions.xlsx", content)
    if not parsed_questions:
        raise HTTPException(
            status_code=400,
            detail="No valid multiple-choice questions found in uploaded document."
        )

    res = mcq_service.bulk_insert_mcqs(parsed_questions, batch_filename=file.filename or "Question Upload")
    total_in_pool = mcq_service.get_total_questions_count()
    approved_in_pool = mcq_service.get_approved_questions_count()

    return {
        "status": "success",
        "uploaded_file": file.filename,
        "batch_id": res["batch_id"],
        "upload_time": res["upload_time"],
        "questions_parsed": len(parsed_questions),
        "questions_inserted": res["inserted_count"],
        "total_pool_count": total_in_pool,
        "approved_pool_count": approved_in_pool
    }


@router.get("/questions")
def get_mcq_questions(
    batch_id: str = "all",
    approval_status: str = "all",
    current_user: dict = Depends(require_role(["staff", "hod"]))
):
    """
    Lists all MCQ questions with their options, correct answers, batch timestamps,
    and approval states for Staff/HOD question verification.
    """
    return mcq_service.get_all_questions(batch_id=batch_id, approval_status=approval_status)


@router.get("/batches")
def get_mcq_batches(
    current_user: dict = Depends(require_role(["staff", "hod"]))
):
    """
    Returns all upload batches with their timestamps and question counts.
    """
    return mcq_service.get_upload_batches()


@router.put("/questions/{question_id}")
def update_mcq_question(
    payload: UpdateQuestionRequest,
    question_id: str = Path(..., description="ID of question to update"),
    current_user: dict = Depends(require_role(["staff", "hod"]))
):
    """
    Allows Staff/HOD to modify question prompt, options, correct answer, explanation, and approval.
    """
    return mcq_service.update_question(
        question_id=question_id,
        question_text=payload.question_text,
        options=payload.options,
        correct_answer=payload.correct_answer,
        explanation=payload.explanation,
        topic=payload.topic,
        is_approved=payload.is_approved
    )


@router.patch("/questions/{question_id}/approve")
def toggle_question_approval(
    question_id: str = Path(..., description="ID of question to approve/unapprove"),
    payload: Optional[ApprovalToggleRequest] = None,
    current_user: dict = Depends(require_role(["staff", "hod"]))
):
    """
    Toggles verified & approved status so only verified questions enter exams.
    """
    is_approved = payload.is_approved if payload is not None else True
    return mcq_service.toggle_question_approval(question_id, is_approved)


@router.delete("/questions/{question_id}")
def delete_mcq_question(
    question_id: str = Path(..., description="ID of question to delete"),
    current_user: dict = Depends(require_role(["staff", "hod"]))
):
    """
    Deletes an individual question from the question bank.
    """
    deleted = mcq_service.delete_question(question_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Question '{question_id}' not found.")
    return {"status": "success", "deleted_count": 1, "message": f"Question '{question_id}' deleted."}


@router.delete("/batches/{batch_id}")
def delete_mcq_batch(
    batch_id: str = Path(..., description="ID of the upload batch to delete"),
    current_user: dict = Depends(require_role(["staff", "hod"]))
):
    """
    Deletes all questions belonging to a specific upload batch timestamp.
    """
    count = mcq_service.delete_batch(batch_id)
    return {"status": "success", "deleted_count": count, "message": f"Deleted {count} questions from batch '{batch_id}'."}


@router.post("/session/start")
def start_mcq_session(
    current_user: dict = Depends(get_current_user)
):
    """
    Initializes a new MCQ assessment session for the student:
    - Selects exactly 20 questions randomized student-by-student.
    - Shuffles option choices per question.
    - Resets proctored strike counter to 0.
    """
    student_id = current_user.get("user_id") or current_user.get("sub")
    student_name = current_user.get("name") or "Candidate"
    session = mcq_service.create_shuffled_session(
        student_id=student_id,
        student_name=student_name,
        count=20
    )
    return session


@router.post("/session/{session_id}/strike")
def record_proctoring_strike(
    session_id: str = Path(..., description="Active session ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    Records a focus loss / cursor out-of-focus event.
    Returns current strikes and flags disqualification when strikes reach 3.
    """
    return mcq_service.record_strike(session_id)


@router.post("/session/{session_id}/submit")
def submit_mcq_session(
    payload: SubmitAnswersRequest,
    session_id: str = Path(..., description="Active session ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    Submits candidate answers for grading:
    - Rejects submission with 403 if candidate received 3 proctoring strikes.
    - Computes score and percentage.
    - Persists results for student, faculty, and HOD dashboards.
    """
    return mcq_service.submit_answers(session_id, payload.answers)


@router.get("/results/all")
def get_all_results(
    current_user: dict = Depends(require_role(["staff", "hod"]))
):
    """Returns all completed candidate MCQ assessment records for faculty/HOD oversight."""
    return mcq_service.get_all_results()


@router.get("/results/my")
def get_my_results(
    current_user: dict = Depends(require_role(["student"]))
):
    """Returns past MCQ assessment records for the authenticated student."""
    student_id = current_user.get("user_id") or current_user.get("sub")
    return mcq_service.get_student_results(student_id)


@router.get("/questions/count")
def get_questions_count(
    current_user: dict = Depends(get_current_user)
):
    """Returns the total number of MCQ questions in the pool."""
    return {"count": mcq_service.get_total_questions_count()}
