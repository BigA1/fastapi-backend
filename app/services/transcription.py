import os
from fastapi import UploadFile
import openai
from typing import Optional

class TranscriptionService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def transcribe_audio(self, audio_file: UploadFile) -> Optional[str]:
        try:
            # Save the uploaded file temporarily
            temp_path = f"temp_{audio_file.filename}"
            with open(temp_path, "wb") as buffer:
                content = await audio_file.read()
                buffer.write(content)

            # Transcribe using Whisper API
            with open(temp_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )

            # Clean up the temporary file
            os.remove(temp_path)

            return transcript.text
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            return None 