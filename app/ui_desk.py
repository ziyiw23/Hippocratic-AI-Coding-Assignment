import os
import streamlit as st
from story_engine import StoryOrchestrator
from app.state import get_api_key


def render_desk(audio_url: str):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(
            """
            <div class="desk-header">
                <h1>The Bedtime Storyteller</h1>
                <p style='font-style:italic; opacity:0.8;'>Whisper a prompt into the inkwell...</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        prompt = st.text_area(
            "Prompt",
            value=st.session_state.selected_prompt,
            height=100,
            placeholder="A brave rabbit who wants to fly to the moon...",
            label_visibility="collapsed",
        )

        if st.button("✨ Weave My Story ✨", use_container_width=True):
            api_key = get_api_key()
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
                    result = engine.run(
                        prompt.strip(),
                        genre=st.session_state.genre,
                        length=st.session_state.length.lower(),
                        retries=max(0, st.session_state.judge_passes - 1),
                    )
                except Exception as e:
                    st.error(f"Error: {e}")
                    return

            base_image = getattr(result, "image_url", None) or "https://placehold.co/600x600/2a1b15/e8d5b0/png?text=Story+Image"
            feedback_history = [
                {
                    "approved": fb.approved,
                    "critique": fb.critique,
                    "score": fb.score,
                }
                for fb in getattr(result, "feedback_history", [])
            ]
            final_feedback = getattr(result, "feedback", None)
            st.session_state.story_data = {
                "title": "The Generated Tale",
                "content": result.final_story,
                "image_url": base_image,
                "judge_critique": getattr(result, "judge_critique", "Approved"),
                "judge_feedback": feedback_history,
                "judge_score": getattr(final_feedback, "score", None),
                "judge_iterations": getattr(result, "iterations", 0),
            }
            st.session_state.pages = _split_text_into_pages(result.final_story)
            st.session_state.page_images = {i: base_image for i in range(len(st.session_state.pages))}
            st.session_state.current_page = 0
            st.session_state.view = "book"
            st.rerun()

        st.markdown("<br><p style='text-align:center; opacity:0.7;'>— Or choose a story card —</p>", unsafe_allow_html=True)
        cols = st.columns(3)
        for i, sugg in enumerate(st.session_state.suggestions):
            with cols[i]:
                if st.button(sugg, use_container_width=True):
                    st.session_state.selected_prompt = sugg
                    st.rerun()

        if st.button("🎲 Shuffle Cards"):
            _refresh_suggestions()
            st.rerun()


def _refresh_suggestions():
    if not get_api_key():
        st.warning("Need API Key for fresh ideas!")
        return
    try:
        from openai import OpenAI

        client = OpenAI(api_key=get_api_key())
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Return a JSON list of 3 short, whimsical children's story prompts."},
                {"role": "user", "content": "Give me 3 new ideas."},
            ],
            temperature=0.9,
        )
        content = response.choices[0].message.content
        if "[" in content:
            import json

            st.session_state.suggestions = json.loads(content[content.find("[") : content.rfind("]") + 1])
    except Exception as e:
        st.error(f"Could not fetch ideas: {e}")


def _split_text_into_pages(text: str, chars_per_page: int = 400):
    paragraphs = text.split("\n\n")
    pages = []
    current_page = ""
    for para in paragraphs:
        if len(current_page) + len(para) > chars_per_page:
            if current_page:
                pages.append(current_page.strip())
                current_page = ""
            if len(para) > chars_per_page:
                words = para.split(" ")
                temp_page = ""

                def flush_temp():
                    nonlocal temp_page
                    if temp_page.strip():
                        pages.append(temp_page.strip())
                    temp_page = ""

                for word in words:
                    if not word:
                        continue
                    if len(word) > chars_per_page:
                        flush_temp()
                        for i in range(0, len(word), chars_per_page):
                            pages.append(word[i : i + chars_per_page])
                        continue

                    candidate = f"{temp_page} {word}".strip() if temp_page else word
                    if len(candidate) > chars_per_page:
                        flush_temp()
                        temp_page = word
                    else:
                        temp_page = candidate

                flush_temp()
                current_page = ""
            else:
                current_page = para
        else:
            current_page += "\n\n" + para
    if current_page.strip():
        pages.append(current_page.strip())
    return pages or [text]
