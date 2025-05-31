from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.core.auth import get_current_user
from app.services.transcription import TranscriptionService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
transcription_service = TranscriptionService()

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """Transcribe an audio file to text."""
    try:
        logger.info(f"Transcribing audio file: {file.filename}")
        result = await transcription_service.transcribe_audio(file)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to transcribe audio")
        return {"text": result}
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) 