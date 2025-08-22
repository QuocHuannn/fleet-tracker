# FastAPI Application Entry Point
# File này khởi tạo FastAPI app và cấu hình các middleware

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# TODO: Import các modules
# from .api import router
# from .database import init_db
# from .config import settings

app = FastAPI(
    title="Fleet Tracker API",
    description="Real-time GPS vehicle tracking system API",
    version="1.0.0",
    contact={
        "name": "Trương Quốc Huân",
        "email": "truonghuan0709@gmail.com",
        "url": "https://github.com/QuocHuannn"
    }
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure proper origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Fleet Tracker API",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "Fleet Tracker Backend",
        "version": "1.0.0"
    }

# TODO: Include routers
# app.include_router(router, prefix="/api/v1")

# TODO: Add startup/shutdown events
# @app.on_event("startup")
# async def startup():
#     await init_db()

# @app.on_event("shutdown") 
# async def shutdown():
#     pass
