"""Streamlit frontend for the internal FastAPI Telugu TTS endpoint."""

import os

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8080")
TTS_ENDPOINT = f"{BACKEND_URL.rstrip('/')}/api/v1/tts/telugu"

st.set_page_config(page_title="Telugu Text to Speech", page_icon="🔊")
st.title("Telugu Text to Speech")
st.caption("Synthesized with Google Cloud Text-to-Speech")

text = st.text_area(
    "Telugu script",
    value="తిరుచ్చి శ్రీ రంగనాథస్వామి ఆలయం",
    height=220,
    placeholder="మీ తెలుగు వచనాన్ని ఇక్కడ ఇవ్వండి...",
)
speaking_rate = st.slider("Speaking rate", min_value=0.25, max_value=2.0, value=1.0, step=0.05)

if st.button("Generate audio", type="primary"):
    if not text.strip():
        st.warning("Please enter Telugu text first.")
    else:
        response = None
        try:
            with st.spinner("Generating audio..."):
                response = requests.post(
                    TTS_ENDPOINT,
                    json={"text": text, "speaking_rate": speaking_rate},
                    timeout=120,
                )
            response.raise_for_status()
        except requests.RequestException as exc:
            detail = response.text if response is not None else str(exc)
            st.error(f"Audio generation failed: {detail}")
        else:
            st.audio(response.content, format="audio/mpeg")
            st.download_button(
                "Download MP3",
                data=response.content,
                file_name="telugu-speech.mp3",
                mime="audio/mpeg",
            )
