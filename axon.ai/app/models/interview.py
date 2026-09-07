from typing import Optional, Any
from pydantic import BaseModel, Field


class StartInterviewRequest(BaseModel):
    candidate_id: str = Field(description="Unique candidate resume ID in ChromaDB")
    student_name: str = Field(default="Candidate", description="Student or candidate name")
    mode: str = Field(default="practice", description="'practice' or 'graded'")
    role_track: str = Field(default="Software Engineer", description="Target role (e.g., Python Developer, Java Architect)")
    target_skill: Optional[str] = Field(default=None, description="Optional remediation skill to focus on")
    max_questions: int = Field(default=25, ge=1, le=50, description="Total number of questions for session")


class StartInterviewResponse(BaseModel):
    session_id: str
    mode: str
    status: str
    current_turn: int
    max_questions: int
    first_question: str
    based_on_topic: str


class SubmitAnswerRequest(BaseModel):
    answer: str = Field(description="Candidate's technical answer")


class TurnEvaluation(BaseModel):
    score: float = Field(description="Numerical grade between 1.0 and 10.0")
    technical_accuracy: str = Field(description="Evaluation of technical correctness")
    areas_for_improvement: str = Field(description="Specific feedback on gaps or omitted details")
    feedback: str = Field(description="Constructive guidance for candidate")
    difficulty_level: int = Field(description="Difficulty level at which question was posed")


class SubmitAnswerResponse(BaseModel):
    session_id: str
    turn_completed: int
    max_questions: int
    is_completed: bool
    evaluation: Optional[TurnEvaluation] = None
    next_question: Optional[str] = None


class SessionHistoryItem(BaseModel):
    turn: int
    question: str
    answer: Optional[str] = None
    evaluation: Optional[TurnEvaluation] = None
    difficulty_level: int


class InterviewStateResponse(BaseModel):
    session_id: str
    candidate_id: str
    student_name: str
    mode: str
    status: str
    current_turn: int
    max_questions: int
    difficulty_level: int
    history: list[SessionHistoryItem]


class SynthesisResponse(BaseModel):
    session_id: str
    mode: str
    overall_score: float
    technical_depth: float
    logical_reasoning: float
    communication_clarity: float
    domain_scores: dict[str, float]
    strengths: list[str]
    weaknesses: list[str]
    roadmap: list[dict[str, Any]]
    tasks_auto_closed: list[str]
