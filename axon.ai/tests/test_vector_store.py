from app.services.chunker import create_chunks
from app.services.vector_store import store_chunks, query_chunks

sections = {
    "education": "B.Tech Information Technology",
    "skills": "Python Java React FastAPI",
    "projects": "Axon AI Recruiter"
}

chunks = create_chunks("candidate123", sections)

store_chunks(chunks)

results = query_chunks(
    "candidate123",
    "React developer",
    top_k=2
)

print(results)