from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import memories, media, transcription
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="Storee API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(memories.router, prefix="/api/memories", tags=["memories"])
app.include_router(media.router, prefix="/api/media", tags=["media"])
app.include_router(transcription.router, prefix="/api/transcription", tags=["transcription"])

@app.get("/")
async def root():
    return {"message": "Welcome to Storee API"}
