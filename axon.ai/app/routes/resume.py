from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import UploadResponse
from app.services.pdf_parser import (
    extract_text_from_pdf,
    split_into_sections,
    ResumeParsingError,
)
from app.services.chunker import create_chunks
from app.services.vector_store import store_chunks

import uuid

router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)


@router.post("/upload", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...)):

    # Check file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # Read uploaded PDF
    file_bytes = await file.read()

    # Generate unique candidate id
    candidate_id = str(uuid.uuid4())

    try:
        # Extract text from PDF
        text = extract_text_from_pdf(file_bytes)

        # Split into sections
        sections = split_into_sections(text)

    except ResumeParsingError as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )

    # Create chunks
    chunks = create_chunks(
        candidate_id,
        sections
    )

    # Store embeddings into ChromaDB
    store_chunks(chunks)

    # Return response
    return UploadResponse(
        candidate_id=candidate_id,
        message="Resume uploaded successfully",
        chunks_created=len(chunks),
        sections_found=list(sections.keys())
    )