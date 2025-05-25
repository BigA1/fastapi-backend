from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.transcription import TranscriptionService

router = APIRouter()
transcription_service = TranscriptionService()

@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    if not audio.filename.endswith(('.wav', '.mp3', '.m4a', '.webm')):
        raise HTTPException(status_code=400, detail="Only WAV, MP3, M4A, and WEBM files are supported")
    
    print(f"Received audio file: {audio.filename}, content type: {audio.content_type}")
    transcript = await transcription_service.transcribe_audio(audio)
    if transcript is None:
        raise HTTPException(status_code=500, detail="Failed to transcribe audio")
    
    return {"text": transcript} 