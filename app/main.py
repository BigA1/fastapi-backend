from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api import stories, media
from app.api.endpoints import transcription
from dotenv import load_dotenv
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Storee API",
    description="API for the Storee application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including PATCH
    allow_headers=["*"],
)

# Include routers
app.include_router(stories.router, prefix="/api/stories", tags=["stories"])
app.include_router(media.router, prefix="/api/media", tags=["media"])
app.include_router(transcription.router, prefix="/api/transcription", tags=["transcription"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Storee API"}
