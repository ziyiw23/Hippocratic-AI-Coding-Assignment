import os
import json
import base64
from typing import List
import streamlit as st
import streamlit.components.v1 as components
from story_engine import ImageGenerator, StoryOrchestrator

# --- CONFIGURATION ---
st.set_page_config(page_title="The Antique Storybook", page_icon="🕯️", layout="wide")

# --- ASSETS ---
MUSIC_TRACKS = {
    "✨ Magical Forest": "musics/quirky-children-music-349960.mp3",
    "🎹 Gentle Piano": "musics/soft-background-piano-285589.mp3",
    "🌧️ Cozy Rain": "musics/in-the-room-when-the-rain-pouring-117209.mp3",
    "🤫 Silence": ""
}

# --- SESSION STATE ---
if "view" not in st.session_state:
    st.session_state.view = "desk"
if "current_page" not in st.session_state:
    st.session_state.current_page = 0
if "pages" not in st.session_state:
    st.session_state.pages = []
if "story_data" not in st.session_state:
    st.session_state.story_data = {}
if "page_images" not in st.session_state:
    st.session_state.page_images = {}
if "selected_prompt" not in st.session_state:
    st.session_state.selected_prompt = ""
if "suggestions" not in st.session_state:
    st.session_state.suggestions = [
        "A tiny dragon who breathes bubbles instead of fire...",
        "The library where books whisper their stories at night...",
        "A squirrel who opens a bakery for the forest animals..."
    ]
if "audio_b64" not in st.session_state:
    st.session_state.audio_b64 = ""

image_generator = ImageGenerator()

# --- HELPERS ---
def split_text_into_pages(text: str, chars_per_page: int = 380) -> List[str]:
    paragraphs = text.split('\n\n')
    pages = []
    current_page = ""
    for para in paragraphs:
        if len(current_page) + len(para) > chars_per_page:
            if current_page:
                pages.append(current_page.strip())
                current_page = ""
            if len(para) > chars_per_page:
                words = para.split(' ')
                temp_page = ""
                for word in words:
                    if len(temp_page) + len(word) > chars_per_page:
                        pages.append(temp_page.strip())
                        temp_page = word
                    else:
                        temp_page += " " + word
                current_page = temp_page
            else:
                current_page = para
        else:
            current_page += "\n\n" + para
    if current_page.strip():
        pages.append(current_page.strip())
    return pages or [text]

def escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_audio_b64(path: str) -> str:
    if not path:
        return ""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return ""

def get_new_suggestions():
    """Calls LLM to get 3 fresh story ideas."""
    if not os.getenv("OPENAI_API_KEY"):
        st.warning("Need API Key for fresh ideas!")
        return
        
    try:
        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Return a JSON list of 3 short, whimsical children's story prompts (1 sentence each)."},
                {"role": "user", "content": "Give me 3 new ideas."}
            ],
            temperature=0.9
        )
        content = response.choices[0].message.content
        if "[" in content and "]" in content:
            import json
            st.session_state.suggestions = json.loads(content[content.find("["):content.rfind("]")+1])
        else:
            st.session_state.suggestions = [line.strip("- *") for line in content.split("\n") if line.strip()][:3]
    except Exception as e:
        st.error(f"Could not fetch ideas: {e}")

def set_prompt(text):
    st.session_state.selected_prompt = text

# --- GLOBAL STYLES & ANIMATIONS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap');
    
    /* --- ANIMATION DEFINITIONS --- */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-6px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes pulse-glow {
        0% { box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(212, 175, 55, 0); }
        100% { box-shadow: 0 0 0 0 rgba(212, 175, 55, 0); }
    }
    
    @keyframes firefly-move {
        0% { transform: translate(0, 0); opacity: 0; }
        20% { opacity: 1; }
        50% { opacity: 0.5; }
        80% { opacity: 1; }
        100% { transform: translate(100px, -150px); opacity: 0; }
    }

    /* BACKGROUND */
    .stApp {
        background-color: #1a1614;
        background-image: repeating-linear-gradient(45deg, rgba(0,0,0,0.05) 0px, rgba(0,0,0,0.05) 2px, transparent 2px, transparent 4px),
                          linear-gradient(to bottom, #2b2118, #1a120b);
    }
    
    /* SIDEBAR STYLING - FIXED ICON ISSUE */
    section[data-testid="stSidebar"] {
        background-color: #261C15;
        border-right: 1px solid #4a3b2a;
    }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label {
        color: #e8d5b0 !important;
        font-family: 'Cormorant Garamond', serif !important;
    }
    section[data-testid="stSidebar"] h1 {
        color: #d4af37 !important;
        font-family: 'Cinzel', serif !important;
    }
    
    /* TYPOGRAPHY */
    h1, h2, h3 { font-family: 'Cinzel', serif !important; color: #d4af37 !important; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }
    p, div, label, input, textarea { font-family: 'Cormorant Garamond', serif !important; color: #f2e6cf; font-size: 1.1rem; }
    
    /* DESK HEADER (With Float Animation) */
    .desk-header {
        background: rgba(20, 15, 10, 0.90);
        border: 1px solid #4a3b2a;
        padding: 30px;
        border-radius: 10px;
        box-shadow: 0 0 40px rgba(0,0,0,0.8);
        text-align: center;
        margin-bottom: 20px;
        animation: float 6s ease-in-out infinite; /* <--- Floating effect */
    }

    /* SUGGESTION CARDS */
    .suggestion-btn {
        border: 1px solid #4a3b2a;
        padding: 10px;
        border-radius: 5px;
        background: rgba(0,0,0,0.3);
        cursor: pointer;
    }
    
    /* BUTTONS (With Hover Transitions) */
    .stButton button {
        background: linear-gradient(to bottom, #3e2b1f, #2a1b15);
        color: #d4af37;
        border: 1px solid #8b6c42;
        font-family: 'Cinzel', serif;
        font-size: 1.0rem;
        margin-top: 10px;
        transition: all 0.3s ease; /* <--- Smooth hover */
    }
    .stButton button:hover {
        border-color: #ffd700;
        color: #fff;
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.4);
    }
    
    /* FIREFLIES CONTAINER */
    .firefly {
        position: fixed;
        width: 4px;
        height: 4px;
        background-color: #ffd700;
        border-radius: 50%;
        box-shadow: 0 0 10px #ffd700;
        pointer-events: none;
        z-index: 0;
        opacity: 0;
    }
    
    /* HIDE FOOTER ONLY */
    footer {visibility: hidden;}
    </style>
    
    <div class="firefly" style="top: 80%; left: 10%; animation: firefly-move 8s infinite alternate;"></div>
    <div class="firefly" style="top: 60%; left: 20%; animation: firefly-move 12s infinite alternate-reverse;"></div>
    <div class="firefly" style="top: 70%; left: 80%; animation: firefly-move 10s infinite alternate;"></div>
    <div class="firefly" style="top: 90%; left: 90%; animation: firefly-move 15s infinite alternate-reverse;"></div>
    <div class="firefly" style="top: 50%; left: 50%; animation: firefly-move 20s infinite alternate;"></div>
    """,
    unsafe_allow_html=True,
)

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuration")
    
    # API Key Input
    api_key_input = st.text_input("OpenAI API Key", type="password", help="Leave blank if using .env")
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input

    st.markdown("---")
    
    # AUDIO TOGGLE
    audio_enabled = st.toggle("🎵 Ambience", value=True)
    
    audio_url = None
    st.session_state.audio_b64 = ""
    if audio_enabled:
        selected_music = st.selectbox("Track", options=list(MUSIC_TRACKS.keys()), index=0, label_visibility="collapsed")
        audio_url = MUSIC_TRACKS[selected_music]
        st.session_state.audio_b64 = load_audio_b64(audio_url)

    st.markdown("---")
    
    writer_temp = st.slider("Creativity", 0.2, 1.0, 0.85, 0.05)
    judge_temp = st.slider("Strictness", 0.0, 0.4, 0.15, 0.01)
    retries = st.slider("Refinement Cycles", 0, 3, 2, 1)

# --- VIEW: DESK ---
def show_desk():
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.markdown("""
        <div class="desk-header">
            <h1>The Bedtime Storyteller</h1>
            <p style='font-style:italic; opacity:0.8; margin-top:10px;'>
                Whisper a prompt into the inkwell...
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # PROMPT INPUT
        prompt = st.text_area(
            "Prompt",
            value=st.session_state.selected_prompt,
            height=100,
            placeholder="A brave rabbit who wants to fly to the moon...",
            label_visibility="collapsed"
        )
        
        # GENERATE BUTTON
        if st.button("✨ Write Story ✨", use_container_width=True):
            if not prompt.strip():
                st.warning("Please enter a story idea first.")
                return
            
            if not os.getenv("OPENAI_API_KEY"):
                st.error("Please provide an OpenAI API Key in the sidebar.")
                return
            
            with st.spinner("Dip pen in ink... summoning the muses..."):
                engine = StoryOrchestrator(writer_temperature=writer_temp, judge_temperature=judge_temp)
                try:
                    result = engine.run(prompt.strip(), retries=retries)
                except Exception as exc:
                    st.error(f"Generation failed: {exc}")
                    return
            
            base_image = getattr(result, "image_url", None)
            if not base_image:
                base_image = f"https://placehold.co/600x600/2a1b15/e8d5b0/png?text=Story+Image"

            st.session_state.story_data = {
                "title": "The Tale of " + (prompt.split(" ")[1] if len(prompt.split()) > 1 else "Wonder"),
                "content": result.final_story,
                "image_url": base_image,
            }
            st.session_state.pages = split_text_into_pages(result.final_story)
            st.session_state.page_images = {i: base_image for i in range(len(st.session_state.pages))}
            st.session_state.current_page = 0
            st.session_state.view = "book"
            st.rerun()

        # --- SUGGESTIONS SECTION ---
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center; font-size:18px;'>Need Inspiration?</h3>", unsafe_allow_html=True)
        
        sc1, sc2, sc3 = st.columns(3)
        suggestions = st.session_state.suggestions
        
        with sc1:
            if st.button(suggestions[0], use_container_width=True):
                set_prompt(suggestions[0])
                st.rerun()
        with sc2:
            if st.button(suggestions[1], use_container_width=True):
                set_prompt(suggestions[1])
                st.rerun()
        with sc3:
            if st.button(suggestions[2], use_container_width=True):
                set_prompt(suggestions[2])
                st.rerun()

        st.markdown("<div style='text-align:center; margin-top:10px;'>", unsafe_allow_html=True)
        if st.button("🎲 Refresh Ideas", help="Ask the AI for new prompts"):
            get_new_suggestions()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# --- VIEW: BOOK ---
def show_book():
    if not st.session_state.pages:
        st.session_state.view = "desk"
        st.rerun()
        return

    pages = st.session_state.pages
    curr = st.session_state.current_page
    data = st.session_state.story_data
    img_url = st.session_state.page_images.get(curr, data["image_url"])
    
    page_text = escape_html(pages[curr]).replace("\n\n", "<br/><br/>").replace("\n", "<br/>")
    
    # HTML BOOK (NOW WITH INTERIOR ANIMATIONS)
    book_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    <style>
        body {{
            background: transparent; margin: 0; padding: 0;
            display: flex; justify-content: center; align-items: center;
            height: 100vh; overflow: hidden;
            font-family: 'Cormorant Garamond', serif;
        }}
        
        /* Entrance Animation for the whole book */
        @keyframes zoomIn {{
            from {{ opacity: 0; transform: scale(0.9); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}
        
        .book {{
            position: relative;
            width: 850px; height: 580px;
            background-color: #fdfbf7;
            background-image: repeating-linear-gradient(transparent, transparent 29px, rgba(0,0,0,0.05) 29px, rgba(0,0,0,0.05) 30px);
            box-shadow: inset 30px 0 50px rgba(0,0,0,0.1), 0 20px 50px rgba(0,0,0,0.6);
            border-radius: 5px 15px 15px 5px;
            display: flex; overflow: hidden;
            border: 8px solid #3e2b1f; border-left: 20px solid #2a1b15;
            animation: zoomIn 0.8s ease-out; /* Book entrance */
        }}

        /* Page Turn Animation */
        @keyframes pageFade {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .page-left {{
            flex: 1; padding: 40px 40px 40px 50px;
            color: #2b1c0f; font-size: 20px; line-height: 1.6;
            position: relative;
            animation: pageFade 0.6s ease-out; /* Triggers on every page change */
        }}
        .page-right {{
            flex: 1; padding: 30px;
            display: flex; align-items: center; justify-content: center;
            background: rgba(245, 240, 230, 0.3);
            animation: pageFade 0.8s ease-out; /* Image fades in slightly slower */
        }}
        .illustration {{
            border: 5px double #8b6c42;
            padding: 5px; background: white;
            box-shadow: 2px 4px 10px rgba(0,0,0,0.2);
            max-width: 90%; max-height: 400px;
            transform: rotate(1deg);
            mix-blend-mode: multiply;
            transition: transform 0.5s ease;
        }}
        .illustration:hover {{
            transform: rotate(0deg) scale(1.02);
        }}
        .drop-cap::first-letter {{
            font-family: 'Cinzel', serif; font-size: 3.5em; float: left;
            line-height: 0.8; margin-right: 0.1em; color: #8b6c42;
        }}
        .page-num {{
            position: absolute; bottom: 20px; width: 100%; text-align: center; color: #888; font-family: 'Cinzel', serif;
        }}
    </style>
    </head>
    <body>
        <div class="book">
            <div class="page-left">
                <div class="{ 'drop-cap' if curr == 0 else '' }">
                    {page_text}
                </div>
                <div class="page-num">- {curr + 1} -</div>
            </div>
            <div class="page-right">
                <img src="{img_url}" class="illustration" alt="Illustration">
            </div>
        </div>
    </body>
    </html>
    """
    
    components.html(book_html, height=650, scrolling=False)

    # Navigation
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns([1, 1, 1, 1, 1])
    with c2:
        if st.button("⬅️ Previous", disabled=curr == 0):
            st.session_state.current_page = max(0, curr - 1)
            st.rerun()
    with c3:
        if st.button("📜 Close Book"):
            st.session_state.view = "desk"
            st.rerun()
    with c4:
        if st.button("Next ➡️", disabled=curr >= len(pages) - 1):
            st.session_state.current_page = min(len(pages) - 1, curr + 1)
            st.rerun()
            
    # Audio Player
    if st.session_state.audio_b64:
        audio_tag = f"""
            <audio autoplay loop id="bg-audio">
                <source src="data:audio/mp3;base64,{st.session_state.audio_b64}" type="audio/mp3">
            </audio>
            <script>
                const audio = document.getElementById("bg-audio");
                if (audio) {{ audio.volume = 0.25; }}
            </script>
        """
        st.markdown(audio_tag, unsafe_allow_html=True)

# --- MAIN ROUTER ---
if st.session_state.view == "desk":
    show_desk()
else:
    show_book()