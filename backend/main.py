# نقطة الدخول الرئيسية - Morix Platform Backend
import warnings
warnings.filterwarnings("ignore", ".*bcrypt.*")
warnings.filterwarnings("ignore", ".*error reading bcrypt version.*")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, manager, student, ai, teacher, owner, admin
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Morix API",
    description="منصة Morix للتعلم الذكي - API",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error: {traceback.format_exc()}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(manager.router, prefix="/api/v1")
app.include_router(student.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(teacher.router, prefix="/api/v1")
app.include_router(owner.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "Morix", "version": settings.app_version}


@app.get("/")
async def root():
    return {"message": "مرحباً بك في Morix API - منصة التعلم الذكي", "docs": "/docs"}
