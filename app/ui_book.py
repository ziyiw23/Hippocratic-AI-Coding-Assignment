import streamlit as st
import streamlit.components.v1 as components
from story_engine import StoryGenerator
from app.audio import build_audio_block
from app.state import get_api_key
from app.ui_desk import _split_text_into_pages


def render_book(audio_url: str, generate_audio_fn):
    anim_mode = st.session_state.get("animation_mode", None)
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

    if anim_mode == "closing":
        try:
            critique = st.session_state.get("remix_critique", "Make it better")
            key = get_api_key()
            sg = StoryGenerator(writer_temperature=st.session_state.writer_temp, api_key=key)
            current_full_story = st.session_state.story_data["content"]
            new_version = sg.refine_story(current_full_story, critique)
            st.session_state.story_data["content"] = new_version
            st.session_state.pages = _split_text_into_pages(new_version)
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

    narrator_html = ""
    if st.session_state.narrate_active:
        st.toast("The storyteller is clearing his throat...", icon="🗣️")
        clean = pages[curr].replace("<br>", " ").replace("\n", " ")
        key = get_api_key()
        if key:
            b64 = st.session_state.audio_cache.get(hash(clean))
            if not b64:
                b64 = generate_audio_fn(clean)
            if b64:
                narrator_html = f'<audio id="narrator" autoplay src="data:audio/mp3;base64,{b64}"></audio>'
        else:
            st.error("Missing API Key for Narrator")

    version = st.session_state.audio_version
    music_vol = st.session_state.music_vol
    st.markdown(build_audio_block(audio_url, narrator_html, music_vol, version), unsafe_allow_html=True)


def escape_html(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

