import os
from fastapi import UploadFile
import openai
from typing import Optional
import tempfile

class TranscriptionService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def transcribe_audio(self, audio_file: UploadFile) -> Optional[str]:
        try:
            # Create a temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                # Save the uploaded file temporarily
                input_path = os.path.join(temp_dir, f"input_{audio_file.filename}")
                with open(input_path, "wb") as buffer:
                    content = await audio_file.read()
                    buffer.write(content)

                # Check if the file is too small (less than 1KB)
                if len(content) < 1024:
                    return "No speech detected. Please try recording again."

                # Transcribe using Whisper API
                with open(input_path, "rb") as audio_file:
                    transcript = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="en"  # Force English language
                    )

                # Check if the transcript is empty or just whitespace
                if not transcript.text or transcript.text.strip() == "":
                    return "No speech detected. Please try recording again."

                return transcript.text
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            return None 