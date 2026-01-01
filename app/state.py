import os
import streamlit as st


# Default session values
DEFAULTS = {
    "view": "desk",
    "current_page": 0,
    "pages": [],
    "story_data": {},
    "page_images": {},
    "selected_prompt": "",
    "suggestions": [
        "A tiny dragon who breathes bubbles instead of fire...",
        "The library where books are made of candies...",
        "A squirrel who opens a bakery for the forest animals...",
    ],
    "audio_cache": {},
    "writer_temp": 0.85,
    "judge_temp": 0.15,
    "judge_passes": 3,
    "genre": "🐉 Adventure",
    "length": "medium",
    "animation_mode": None,
    "selected_track": "✨ Magical Forest",
    "audio_enabled": True,
    "audio_b64": "",
    "back_cover_feedback": "",
    "music_vol": 0.2,
    "narrate_active": False,
    "audio_version": 0,
    "user_api_key": os.getenv("OPENAI_API_KEY", ""),
}


def ensure_state():
    for key, val in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = val


def get_api_key() -> str:
    key = st.session_state.get("user_api_key") or os.getenv("OPENAI_API_KEY", "")
    return key.strip()


def set_api_key(val: str):
    st.session_state["user_api_key"] = val.strip()
