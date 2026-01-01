import base64
import os
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.state import ensure_state, get_api_key
from app.styles import FIREFLIES_HTML, STYLE_CSS
from app.ui_back_cover import render_back_cover
from app.ui_book import render_book
from app.ui_desk import render_desk

MUSIC_TRACKS = {
    "✨ Magical Forest": "musics/quirky-children-music-349960.mp3",
    "🎹 Gentle Piano": "musics/soft-background-piano-285589.mp3",
    "🌧️ Cozy Rain": "musics/in-the-room-when-the-rain-pouring-117209.mp3",
}


def generate_audio_for_text(text: str) -> str:
    api_key = get_api_key()
    if not api_key:
        st.error("⚠️ Narrator requires an API Key.")
        return ""
    text_key = hash(text)
    if text_key in st.session_state.audio_cache:
        return st.session_state.audio_cache[text_key]
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.audio.speech.create(model="tts-1", voice="fable", input=text)
        audio_b64 = base64.b64encode(response.content).decode("utf-8")
        st.session_state.audio_cache[text_key] = audio_b64
        return audio_b64
    except Exception as e:
        st.error(f"Narrator Error: {e}")
        return ""


st.set_page_config(page_title="The Antique Storybook", page_icon="🕯️", layout="wide")
ensure_state()
st.markdown(STYLE_CSS + FIREFLIES_HTML, unsafe_allow_html=True)


def load_music_data_url() -> str:
    if not st.session_state.audio_enabled:
        return ""
    track = st.session_state.selected_track
    path = MUSIC_TRACKS.get(track)
    if not path or not os.path.exists(path):
        return ""
    try:
        with open(path, "rb") as f:
            return "data:audio/mp3;base64," + base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""


with st.sidebar:
    st.header("⚙️ Settings")
    st.text_input("API Key", type="password", key="user_api_key")

    st.markdown("---")
    st.toggle("🎵 Ambience", key="audio_enabled")
    if st.session_state.audio_enabled:
        selected = st.selectbox("Track", list(MUSIC_TRACKS.keys()), index=list(MUSIC_TRACKS.keys()).index(st.session_state.selected_track))
        if selected != st.session_state.selected_track:
            st.session_state.selected_track = selected
            st.session_state.audio_version += 1

    st.markdown("---")
    st.selectbox("Genre / Arc", ["🐉 Adventure", "🧚 Fairy Tale", "🌙 Bedtime Calm", "😂 Funny"], key="genre")
    st.slider("Creativity", 0.2, 1.0, key="writer_temp")
    st.slider("Strictness", 0.0, 0.4, key="judge_temp")
    st.slider(
        "Judge Passes",
        min_value=1,
        max_value=5,
        key="judge_passes",
        help="Total number of judge reviews (includes the first pass).",
    )
    st.select_slider("Story Length", options=["short", "medium", "long"], key="length")


audio_url = load_music_data_url()

if st.session_state.view == "desk":
    render_desk(audio_url)
elif st.session_state.view == "book":
    render_book(audio_url, generate_audio_for_text)
else:
    render_back_cover()
