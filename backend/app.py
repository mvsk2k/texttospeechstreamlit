"""Internal FastAPI service used by the Streamlit UI.

Authentication is deliberately not configured here.  On Cloud Run the Google
Cloud Text-to-Speech client automatically uses the service account attached to
the revision (Application Default Credentials).
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from google.api_core.exceptions import GoogleAPICallError
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import texttospeech
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

MAX_CHUNK_BYTES = 1_500
MAX_INPUT_BYTES = 100_000

app = FastAPI(title="Telugu Text-to-Speech API", version="1.0.0")


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to synthesize")
    speaking_rate: float = Field(default=1.0, ge=0.25, le=4.0)


def split_into_safe_chunks(text: str, max_bytes: int = MAX_CHUNK_BYTES) -> list[str]:
    """Split UTF-8 text without exceeding the per-request byte limit.

    Newlines are preferred boundaries; very long lines are then split at
    whitespace when possible, falling back to character boundaries.
    """
    if max_bytes < 1:
        raise ValueError("max_bytes must be positive")

    chunks: list[str] = []
    current = ""

    def append_piece(piece: str) -> None:
        nonlocal current
        candidate = f"{current}\n{piece}".strip() if current else piece
        if len(candidate.encode("utf-8")) <= max_bytes:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = piece

    # Treat each non-empty line as a preferred boundary, then make every long
    # line safe before adding it to the output.
    for line in (item.strip() for item in text.splitlines() if item.strip()):
        remaining = line
        while len(remaining.encode("utf-8")) > max_bytes:
            byte_count = 0
            cut_at = 0
            last_space = 0
            for index, char in enumerate(remaining, start=1):
                char_size = len(char.encode("utf-8"))
                if byte_count + char_size > max_bytes:
                    break
                byte_count += char_size
                cut_at = index
                if char.isspace():
                    last_space = index
            split_at = last_space or cut_at
            append_piece(remaining[:split_at].strip())
            if current:
                chunks.append(current)
                current = ""
            remaining = remaining[split_at:].strip()
        if remaining:
            append_piece(remaining)

    if current:
        chunks.append(current)
    return chunks


@app.get("/healthz")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/tts/telugu", response_class=Response)
def synthesize_telugu(request: TTSRequest) -> Response:
    """Return synthesized Telugu speech as an MP3; no audio is stored on disk."""
    normalized_text = request.text.strip()
    if not normalized_text:
        raise HTTPException(status_code=422, detail="text must contain non-whitespace characters")
    if len(normalized_text.encode("utf-8")) > MAX_INPUT_BYTES:
        raise HTTPException(status_code=413, detail="text exceeds the 100,000-byte limit")

    chunks = split_into_safe_chunks(normalized_text)
    if not chunks:
        raise HTTPException(status_code=422, detail="text must contain speakable content")

    voice = texttospeech.VoiceSelectionParams(
        language_code="te-IN",
        name="te-IN-Standard-A",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=request.speaking_rate,
    )

    try:
        client = texttospeech.TextToSpeechClient()
        audio = bytearray()
        for chunk in chunks:
            result = client.synthesize_speech(
                input=texttospeech.SynthesisInput(text=chunk),
                voice=voice,
                audio_config=audio_config,
            )
            # Consecutive MP3 frame streams can be played as one MP3 by modern
            # players, avoiding a temporary file or an ffmpeg dependency.
            audio.extend(result.audio_content)
    except (GoogleAPICallError, DefaultCredentialsError) as exc:
        logger.exception("Google Cloud Text-to-Speech request failed")
        raise HTTPException(status_code=502, detail="Text-to-Speech service request failed") from exc

    return Response(
        content=bytes(audio),
        media_type="audio/mpeg",
        headers={"Content-Disposition": 'inline; filename="telugu-speech.mp3"'},
    )
