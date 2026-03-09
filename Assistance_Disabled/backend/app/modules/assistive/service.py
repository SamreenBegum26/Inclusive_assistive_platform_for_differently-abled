import os
import whisper
from gtts import gTTS
import uuid
import base64
import io

# ✅ Load whisper model once at startup
model = whisper.load_model("base")


def transcribe_audio(file_path: str, language: str = None) -> str:
    """
    Takes an audio file path, returns transcript text.
    """
    if language:
        result = model.transcribe(file_path, language=language)
    else:
        result = model.transcribe(file_path)

    return result["text"]


def generate_speech_base64(text: str, language: str) -> str:
    """
    Converts text to speech and returns base64 encoded audio string.
    Frontend can play this directly without downloading any file.
    """
    # Generate speech into memory buffer (no file saved!)
    mp3_buffer = io.BytesIO()
    tts = gTTS(text=text, lang=language)
    tts.write_to_fp(mp3_buffer)
    mp3_buffer.seek(0)

    # Convert to base64 string
    audio_base64 = base64.b64encode(mp3_buffer.read()).decode("utf-8")

    return audio_base64