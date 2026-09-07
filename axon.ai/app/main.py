from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.resume import router as resume_router
from app.routes.retrieval import router as retrieval_router
from app.routes.interview import router as interview_router
from app.routes.auth import router as auth_router
from app.routes.tasks import router as tasks_router
from app.services.key_pool import key_pool

app = FastAPI(
    title="Axon AI Recruiter & Assessment Platform",
    description="Adaptive AI-driven technical interviews, key pool rotation, and skill synthesis.",
    version="1.0.0"
)

# Enable CORS for Frontend Development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local dev (localhost:5173, localhost:3000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routes
app.include_router(resume_router)
app.include_router(retrieval_router)
app.include_router(interview_router)
app.include_router(auth_router)
app.include_router(tasks_router)


@app.get("/")
def root():
    return {
        "message": "Axon Backend Running",
        "status": "online",
        "pool_capacity": f"{key_pool.total_keys} Gemini keys ({key_pool.total_keys * 15} RPM max)"
    }


@app.get("/config")
def config():
    return {
        "gemini_model": settings.gemini_model,
        "total_api_keys": key_pool.total_keys,
        "max_upload_size": settings.max_upload_size_mb
    }