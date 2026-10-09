from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.routes.resume import router as resume_router
from app.routes.retrieval import router as retrieval_router
from app.routes.interview import router as interview_router
from app.routes.auth import router as auth_router
from app.routes.tasks import router as tasks_router
from app.routes.mcq import router as mcq_router

app = FastAPI(
    title="Axon AI Recruiter & Assessment Platform",
    description="Adaptive offline technical interviews, recommendation chaining, and skill synthesis.",
    version="1.0.0"
)

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

# Enable CORS for local dev and deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    detail_msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error": detail_msg,
            "status_code": exc.status_code
        },
        headers=exc.headers
    )

# Register API Routes
app.include_router(resume_router)
app.include_router(retrieval_router)
app.include_router(interview_router)
app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(mcq_router)


@app.get("/api/health")
def api_health():
    return {
        "message": "Axon Backend Running (100% Offline Engine)",
        "status": "online",
        "engine": "Algorithmic Keyword-Chain Recommendation Engine",
        "api_keys_required": False
    }

@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/config")
def config():
    return {
        "engine_mode": "offline_keyword_chain",
        "embeddings": "local_sentence_transformers_384d",
        "total_api_keys": 0,
        "max_upload_size": settings.max_upload_size_mb
    }


# Mount and serve built React frontend from axon-ui/dist
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "axon-ui" / "dist"

if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        target = FRONTEND_DIST / full_path
        if full_path and target.is_file():
            return FileResponse(target)
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/")
    def root():
        return api_health()