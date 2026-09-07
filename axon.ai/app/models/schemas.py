from pydantic import BaseModel


class UploadResponse(BaseModel):
    candidate_id: str
    message: str
    chunks_created: int
    sections_found: list[str]


class RetrievalQuery(BaseModel):
    candidate_id: str
    query: str
    top_k: int = 3


class RetrievalResultItem(BaseModel):
    chunk_text: str
    section: str
    score: float


class RetrievalResponse(BaseModel):
    results: list[RetrievalResultItem]


class InterviewRequest(BaseModel):
    candidate_id: str
    topic: str


class InterviewResponse(BaseModel):
    question: str
    based_on_section: str