import os
import json
import base64
import time
from typing import List
import streamlit as st
import streamlit.components.v1 as components
from story_engine import ImageGenerator, StoryOrchestrator, StoryGenerator

# --- CONFIGURATION ---
st.set_page_config(page_title="The Antique Storybook", page_icon="🕯️", layout="wide")

# --- ASSETS ---
# Ensure you have a folder named 'musics' with these files, 
# or the app will simply run without audio.
MUSIC_TRACKS = {
    "✨ Magical Forest": "musics/quirky-children-music-349960.mp3",
    "🎹 Gentle Piano": "musics/soft-background-piano-285589.mp3",
    "🌧️ Cozy Rain": "musics/in-the-room-when-the-rain-pouring-117209.mp3",
}

# --- SESSION STATE INITIALIZATION ---
defaults = {
    "view": "desk",
    "current_page": 0,
    "pages": [],
    "story_data": {},
    "page_images": {},
    "selected_prompt": "",
    "suggestions": [
        "A tiny dragon who breathes bubbles instead of fire...",
        "The library where books are made of candies...",
        "A squirrel who opens a bakery for the forest animals..."
    ],
    "audio_cache": {},
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

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- HELPERS ---
def split_text_into_pages(text: str, chars_per_page: int = 400) -> List[str]:
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

def get_new_suggestions():
    if not st.session_state.get("user_api_key"):
        st.warning("Need API Key for fresh ideas!")
        return
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.session_state.user_api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Return a JSON list of 3 short, whimsical children's story prompts."},
                {"role": "user", "content": "Give me 3 new ideas."}
            ],
            temperature=0.9
        )
        content = response.choices[0].message.content
        if "[" in content:
            st.session_state.suggestions = json.loads(content[content.find("["):content.rfind("]")+1])
    except Exception as e:
        st.error(f"Could not fetch ideas: {e}")

def set_prompt(text):
    st.session_state.selected_prompt = text

def generate_audio_for_text(text: str) -> str:
    api_key = st.session_state.get("user_api_key") or os.getenv("OPENAI_API_KEY")
    # 1. Validation
    if not api_key:
        st.error("⚠️ Narrator requires an API Key.")
        return ""
    # 2. Cache
    text_key = hash(text)
    if text_key in st.session_state.audio_cache:
        return st.session_state.audio_cache[text_key]
    # 3. Call API with error reporting
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

# --- GLOBAL STYLES ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap');

/* ANIMATIONS */
@keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-6px); } 100% { transform: translateY(0px); } }
@keyframes firefly-move { 0% { opacity: 0; } 50% { opacity: 0.8; } 100% { transform: translate(100px, -150px); opacity: 0; } }

/* APP BASE */
.stApp {
    background-color: #1a1614;
    background-image: repeating-linear-gradient(45deg, rgba(0,0,0,0.05) 0px, rgba(0,0,0,0.05) 2px, transparent 2px, transparent 4px),
                      linear-gradient(to bottom, #2b2118, #1a120b);
}

/* TYPOGRAPHY */
h1, h2, h3, h4 { font-family: 'Cinzel', serif !important; color: #d4af37 !important; }
p, label, div, input, textarea { font-family: 'Cormorant Garamond', serif !important; color: #f2e6cf; font-size: 1.1rem; }

/* SIDEBAR */
section[data-testid="stSidebar"] { background-color: #261C15; border-right: 1px solid #4a3b2a; }

/* DESK HEADER & BACK COVER */
.desk-header, .back-cover {
    background: rgba(20, 15, 10, 0.90);
    border: 1px solid #4a3b2a;
    padding: 30px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 0 50px rgba(0,0,0,0.8);
    animation: float 6s ease-in-out infinite;
}

/* CUSTOM WIDGET STYLING */
div[data-baseweb="select"] > div { background-color: rgba(0,0,0,0.3) !important; border-color: #8b6c42 !important; color: white !important; }
.stTextArea textarea { background-color: rgba(0,0,0,0.3) !important; border: 1px solid #8b6c42 !important; color: #e8d5b0 !important; }

/* FIREFLIES */
.firefly { position: fixed; width: 4px; height: 4px; background: #ffd700; border-radius: 50%; box-shadow: 0 0 10px #ffd700; pointer-events: none; opacity: 0; }

/* BUTTONS */
.stButton button {
    background: linear-gradient(to bottom, #3e2b1f, #2a1b15);
    color: #d4af37;
    border: 1px solid #8b6c42;
    font-family: 'Cinzel', serif;
    transition: all 0.3s ease;
}
.stButton button:hover { border-color: #ffd700; color: #fff; transform: scale(1.02); }

/* Remove Footer */
footer {visibility: hidden;}
</style>
<div class="firefly" style="top: 80%; left: 10%; animation: firefly-move 8s infinite alternate;"></div>
<div class="firefly" style="top: 60%; left: 20%; animation: firefly-move 12s infinite alternate-reverse;"></div>
<div class="firefly" style="top: 50%; left: 50%; animation: firefly-move 20s infinite alternate;"></div>
<div class="firefly" style="top: 30%; left: 15%; animation: firefly-move 14s infinite alternate;"></div>
<div class="firefly" style="top: 25%; left: 70%; animation: firefly-move 18s infinite alternate-reverse;"></div>
<div class="firefly" style="top: 85%; left: 60%; animation: firefly-move 16s infinite alternate;"></div>
<div class="firefly" style="top: 40%; left: 85%; animation: firefly-move 22s infinite alternate-reverse;"></div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.text_input("API Key", type="password", help="OpenAI API Key", key="user_api_key")

    st.markdown("---")
    
    # Audio Settings
    audio_enabled = st.toggle("🎵 Ambience", value=True)
    st.session_state.audio_enabled = audio_enabled
    
    audio_url = None
    if audio_enabled:
        current_selection = st.session_state.get("selected_track", "✨ Magical Forest")
        
        track = st.selectbox(
            "Track",
            list(MUSIC_TRACKS.keys()),
            label_visibility="collapsed",
            index=list(MUSIC_TRACKS.keys()).index(current_selection) if current_selection in MUSIC_TRACKS else 0,
        )

        # CHECK FOR CHANGE: Increment version to force reload
        if track != st.session_state.get("selected_track"):
            st.session_state.audio_version += 1
            st.session_state.selected_track = track
            
        if MUSIC_TRACKS.get(track):
            path = MUSIC_TRACKS[track]
            if os.path.exists(path):
                try:
                    with open(path, "rb") as f:
                        st.session_state.audio_b64 = base64.b64encode(f.read()).decode("utf-8")
                except Exception:
                    st.session_state.audio_b64 = ""
            else:
                st.session_state.audio_b64 = ""
        else:
            st.session_state.audio_b64 = ""
            
        if st.session_state.audio_b64:
            audio_url = f"data:audio/mp3;base64,{st.session_state.audio_b64}"

    # st.slider("Music Volume", 0.0, 1.0, step=0.01, key="music_vol")
    
    st.markdown("---")
    st.selectbox("Genre / Arc", ["🐉 Adventure", "🧚 Fairy Tale", "🌙 Bedtime Calm", "😂 Funny"], key="genre")
    st.slider("Creativity", 0.2, 1.0, 0.85, key="writer_temp")
    st.slider("Strictness", 0.0, 0.4, 0.15, key="judge_temp")
    st.select_slider("Story Length", options=["short", "medium", "long"], key="length")
    

# --- VIEW: DESK ---
def show_desk():
    c1, c2, c3 = st.columns([1, 2, 1])
    
    with c2:
        st.markdown("""
        <div class="desk-header">
            <h1>The Bedtime Storyteller</h1>
            <p style='font-style:italic; opacity:0.8;'>Whisper a prompt into the inkwell...</p>
        </div>
        """, unsafe_allow_html=True)
    
        st.markdown("<br>", unsafe_allow_html=True)

        prompt = st.text_area("Prompt", value=st.session_state.selected_prompt, height=100, placeholder="A brave rabbit who wants to fly to the moon...", label_visibility="collapsed")
        
        if st.button("✨ Weave My Story ✨", use_container_width=True):
            api_key = st.session_state.get("user_api_key") or os.getenv("OPENAI_API_KEY")
            if not prompt.strip():
                st.warning("Please enter a prompt.")
                return
            if not api_key:
                st.warning("Please enter an API Key in the sidebar.")
                return
            
            with st.spinner("Summoning the muses..."):
                engine = StoryOrchestrator(
                    writer_temperature=st.session_state.writer_temp,
                    judge_temperature=st.session_state.judge_temp,
                    api_key=api_key,
                )
                try:
                    result = engine.run(prompt.strip(), genre=st.session_state.genre, length=st.session_state.length.lower())
                except Exception as e:
                    st.error(f"Error: {e}")
                    return
            
            base_image = getattr(result, "image_url", None) or "https://placehold.co/600x600/2a1b15/e8d5b0/png?text=Story+Image"
            st.session_state.story_data = {"title": "The Generated Tale", "content": result.final_story, "image_url": base_image}
            st.session_state.pages = split_text_into_pages(result.final_story)
            st.session_state.page_images = {i: base_image for i in range(len(st.session_state.pages))}
            st.session_state.current_page = 0
            st.session_state.view = "book"
            st.rerun()

        st.markdown("<br><p style='text-align:center; opacity:0.7;'>— Or choose a story card —</p>", unsafe_allow_html=True)
        cols = st.columns(3)
        for i, sugg in enumerate(st.session_state.suggestions):
            with cols[i]:
                if st.button(sugg, use_container_width=True):
                    set_prompt(sugg)
                    st.rerun()
        
        if st.button("🎲 Shuffle Cards"):
            get_new_suggestions()
            st.rerun()

# --- VIEW: BOOK ---
def show_book():
    anim_mode = st.session_state.get("animation_mode", None)
    
    # Animation CSS logic
    extra_css = ""
    if anim_mode == "closing":
        extra_css = "animation: bookClose 1.5s forwards;"
    elif anim_mode == "opening":
        extra_css = "animation: bookOpen 1.5s ease-out;"
    else:
        extra_css = "animation: zoomIn 0.6s ease-out;"

    if not st.session_state.pages:
        st.session_state.view = "desk"
        st.rerun()
        return

    pages = st.session_state.pages
    curr = st.session_state.current_page
    img_url = st.session_state.page_images.get(curr, st.session_state.story_data.get("image_url", ""))
    page_text = escape_html(pages[curr]).replace("\n\n", "<br/><br/>")
    
    # HTML BOOK COMPONENT
    book_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    <style>
        body {{ background: transparent; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; font-family: 'Cormorant Garamond', serif; perspective: 1500px; }}
        
        @keyframes zoomIn {{ from {{ opacity: 0; transform: scale(0.95); }} to {{ opacity: 1; transform: scale(1); }} }}
        @keyframes bookClose {{ 0% {{ transform: rotateY(0deg); }} 100% {{ transform: rotateY(-90deg) scale(0.8); opacity: 0; }} }}
        @keyframes bookOpen  {{ 0% {{ transform: rotateY(-90deg) scale(0.8); opacity: 0; }} 100% {{ transform: rotateY(0deg) scale(1); opacity: 1; }} }}

        .book {{
            position: relative;
            width: min(90vw, 850px);
            aspect-ratio: 3 / 2;
            background: #fdfbf7;
            background-image: repeating-linear-gradient(transparent, transparent 29px, rgba(0,0,0,0.05) 29px, rgba(0,0,0,0.05) 30px);
            box-shadow: inset 30px 0 50px rgba(0,0,0,0.1), 0 20px 50px rgba(0,0,0,0.6);
            border-radius: 5px 15px 15px 5px; border: 8px solid #3e2b1f; border-left: 20px solid #2a1b15;
            display: flex; overflow: hidden;
            {extra_css}
        }}
        .page-left {{ flex: 1; padding: 40px 50px; color: #2b1c0f; font-size: 20px; line-height: 1.6; overflow-y: auto; }}
        .page-right {{ flex: 1; padding: 30px; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.03); }}
        .illustration {{ border: 5px double #8b6c42; padding: 5px; background: white; max-width: 90%; max-height: 400px; transform: rotate(1deg); mix-blend-mode: multiply; }}
        .drop-cap::first-letter {{ font-family: 'Cinzel', serif; font-size: 3.5em; float: left; line-height: 0.8; margin-right: 0.1em; color: #8b6c42; }}
        .page-num {{ position: absolute; bottom: 20px; width: 100%; text-align: center; color: #888; font-family: 'Cinzel', serif; }}
        ::-webkit-scrollbar {{ width: 0px; background: transparent; }}
    </style>
    </head>
    <body>
        <div class="book">
            <div class="page-left">
                <div class="{ 'drop-cap' if curr == 0 else '' }">{page_text}</div>
                <div class="page-num">- {curr + 1} -</div>
            </div>
            <div class="page-right">
                <img src="{img_url}" class="illustration">
            </div>
        </div>
    </body>
    </html>
    """
    components.html(book_html, height=650, scrolling=False)

    # REMIX / REWRITE LOGIC
    if anim_mode == "closing":
        try:
            critique = st.session_state.get("remix_critique", "Make it better")
            key = st.session_state.get("user_api_key") or os.getenv("OPENAI_API_KEY")
            sg = StoryGenerator(writer_temperature=st.session_state.writer_temp, api_key=key)
            current_full_story = st.session_state.story_data["content"]
            new_version = sg.refine_story(current_full_story, critique)
            
            st.session_state.story_data["content"] = new_version
            st.session_state.pages = split_text_into_pages(new_version)
            st.session_state.current_page = 0
            
            st.session_state.animation_mode = "opening"
            st.rerun()
        except Exception as e:
            st.error(f"Remix failed: {e}")
            st.session_state.animation_mode = None
            st.rerun()
            
    if anim_mode == "opening":
        st.session_state.animation_mode = None
        st.rerun()

    # --- CONTROLS ---
    st.markdown("<br>", unsafe_allow_html=True)
    c_spacer1, c_prev, c_close, c_read, c_next, c_spacer2 = st.columns([1, 4, 4, 4, 4, 1])
    
    with c_prev:
        if st.button("⬅️ Previous", use_container_width=True, disabled=curr == 0):
            st.session_state.current_page -= 1
            st.rerun()
            
    with c_close:
        if st.button("📜 Close", use_container_width=True):
            st.session_state.view = "desk"
            st.rerun()
            
    with c_read:
        btn_type = "primary" if st.session_state.narrate_active else "secondary"
        if st.button("🗣️ Read Page", type=btn_type, use_container_width=True, help="Toggle voice narration"):
            st.session_state.narrate_active = not st.session_state.narrate_active
            st.rerun()

    with c_next:
        if curr == len(pages) - 1:
            if st.button("The End ➡️", use_container_width=True):
                st.session_state.view = "back_cover"
                st.rerun()
        else:
            if st.button("Next ➡️", use_container_width=True):
                st.session_state.current_page += 1
                st.rerun()

    # --- AUDIO PLAYER & DUCKING ---
    narrator_html = ""
    if st.session_state.narrate_active:
        st.toast("The storyteller is clearing his throat...", icon="🗣️")
        clean = pages[curr].replace("<br>", " ").replace("\n", " ")
        if st.session_state.get("user_api_key") or os.getenv("OPENAI_API_KEY"):
            with st.spinner("Preparing voice..."):
                b64 = generate_audio_for_text(clean)
            if b64:
                narrator_html = f'<audio id="narrator" autoplay src="data:audio/mp3;base64,{b64}"></audio>'
        else:
            st.error("Missing API Key for Narrator")

    version = st.session_state.audio_version
    music_vol = st.session_state.music_vol # This comes from the Slider

    st.markdown(
        f"""
        <div style="display:none;">
            {"<audio autoplay loop id='bg-audio-"+str(version)+"' data-audio-player='bg'><source src='"+audio_url+"' type='audio/mp3'></audio>" if audio_url else ""}
            {narrator_html}
        </div>

        <script>
            (function() {{
                var bg = document.getElementById("bg-audio-{version}");
                var narr = document.getElementById("narrator");
                var userMusicVol = {music_vol}; // The slider value

                // 1. Clean up old players
                document.querySelectorAll('audio[data-audio-player="bg"]').forEach(function(a) {{
                    if (a.id !== "bg-audio-{version}") {{ a.pause(); a.remove(); }}
                }});

                // 2. Clear lingering timers
                if (window.narratorFade) {{ clearInterval(window.narratorFade); window.narratorFade = null; }}

                // 3. Setup BACKGROUND MUSIC (Controlled by Slider)
                if(bg) {{
                    bg.volume = userMusicVol; // Apply slider volume to music
                    bg.play().catch(e => console.log("BG Play Error:", e));
                }}

                // 4. Setup NARRATOR (Independent / Always Full Volume)
                if(narr) {{
                    narr.volume = 1.0; // Force Narrator to 100%, ignoring slider
                    
                    var p = narr.play();
                    if(p) p.catch(e => console.log("Narrator Play Error:", e));
                    
                    if(bg) {{
                        // EVENT: Duck music when narrator starts
                        narr.onplay = function() {{
                            // Drop music to 25% of the SLIDER value
                            bg.volume = Math.max(0, userMusicVol * 0.25);
                        }};

                        // EVENT: Restore music when narrator ends
                        narr.onended = function() {{
                            window.narratorFade = setInterval(function(){{
                                // Fade back up to the SLIDER value, not 100%
                                if(bg.volume < userMusicVol) {{
                                    bg.volume = Math.min(userMusicVol, bg.volume + 0.05);
                                }} else {{
                                    clearInterval(window.narratorFade);
                                }}
                            }}, 100);
                        }};
                    }}
                }}
            }})();
        </script>
        """,
        unsafe_allow_html=True,
    )

# --- VIEW: BACK COVER ---
def show_back_cover():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(f"""
        <div class="back-cover">
            <h1>The End</h1>
            <p>We hope you enjoyed<br><i>{st.session_state.story_data.get('title', 'the story')}</i>.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🪄 Remix the Story")
        st.markdown("Did you like it? Tell the magic book what to change.")
        
        critique = st.text_area("Suggestion Box", placeholder="e.g. Make the ending happier...", label_visibility="collapsed")
        
        b1, b2, b3 = st.columns(3)
        with b1:
             if st.button("📖 Re-read"):
                st.session_state.view = "book"
                st.session_state.current_page = 0
                st.rerun()
        with b2:
            if st.button("✨ Write New"):
                if not critique.strip():
                    st.warning("Please add a suggestion.")
                else:
                    st.session_state.remix_critique = critique
                    st.session_state.animation_mode = "closing" 
                    st.session_state.view = "book"
                    st.rerun()
        with b3:
            story_text = st.session_state.story_data.get("content", "")
            st.download_button("💾 Download", data=story_text, file_name="my_story.txt")

        st.markdown("<br><div style='text-align:center'><a href='#' onclick='window.location.reload()'>Start Over at Desk</a></div>", unsafe_allow_html=True)


# --- ROUTER ---
if st.session_state.view == "desk":
    show_desk()
elif st.session_state.view == "book":
    show_book()
elif st.session_state.view == "back_cover":
    show_back_cover()