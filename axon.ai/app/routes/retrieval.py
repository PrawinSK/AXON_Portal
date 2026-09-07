from fastapi import APIRouter
from app.models.schemas import (
    RetrievalQuery,
    RetrievalResponse,
    RetrievalResultItem
)

from app.services.vector_store import query_chunks

router = APIRouter(
    prefix="/retrieval",
    tags=["Retrieval"]
)


@router.post("/query", response_model=RetrievalResponse)
async def query_resume(payload: RetrievalQuery):

    results = query_chunks(
        payload.candidate_id,
        payload.query,
        payload.top_k
    )

    return RetrievalResponse(
        results=[
            RetrievalResultItem(**r)
            for r in results
        ]
    )