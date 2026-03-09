import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.assistive.models import SpeechLog
from app.modules.assistive.service import transcribe_audio, generate_speech_base64

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ====================================
# STT - SPEECH TO TEXT
# User uploads/records audio → gets transcript on screen
# ====================================
@router.post("/stt")
async def speech_to_text(
    file: UploadFile = File(...),
    language: str = Form(None),       # optional: "en", "hi", "te" etc.
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Save uploaded audio temporarily with unique name
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        # Transcribe audio
        transcript = transcribe_audio(file_path, language)

        # Save log to DB
        log = SpeechLog(
            user_id=current_user.id,
            filename=file.filename,
            transcript=transcript,
            language=language or "auto"
        )
        db.add(log)
        db.commit()

    finally:
        # ✅ Always delete temp file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

    # ✅ Return transcript as JSON - frontend shows it on screen directly
    return {
        "transcript": transcript,
        "language": language or "auto",
        "display": True
    }


# ====================================
# TTS - TEXT TO SPEECH
# User types text → audio plays in browser + text shown on screen
# ====================================
@router.post("/tts")
def text_to_speech(
    text: str = Form(...),
    language: str = Form(...),        # "en", "hi", "te" etc.
    current_user=Depends(get_current_user)
):
    # ✅ Generate audio as base64 (no file saved, no download needed)
    audio_base64 = generate_speech_base64(text, language)

    # ✅ Return both text and audio in JSON
    return {
        "text": text,
        "language": language,
        "audio_base64": audio_base64,
        "audio_format": "audio/mpeg",
        "how_to_play": "data:audio/mpeg;base64," + audio_base64
    }