import streamlit as st
from app.state import get_api_key


def render_back_cover():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown(
            f"""
            <div class="back-cover">
                <h1>The End</h1>
                <p>We hope you enjoyed<br><i>{st.session_state.story_data.get('title', 'the story')}</i>.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 🪄 Remix the Story")
        st.markdown("Did you like it? Tell the magic book what to change.")

        # Educational Easter Egg
        with st.expander("🎓 Parents: Vocabulary & Themes"):
            st.info("This story was safety-checked by our AI Judge.")
            st.caption("Judge scores use a 1–10 scale (higher means better fit for ages 5-10).")
            feedback_items = st.session_state.story_data.get("judge_feedback", [])
            if feedback_items:
                for idx, fb in enumerate(feedback_items, 1):
                    status = "PASS ✅" if fb.get("approved") else "Needs Changes"
                    score = fb.get("score")
                    score_text = f"(score 1-10: {score})" if score is not None else ""
                    critique = fb.get("critique") or "PASS"
                    st.write(f"**Round {idx} {status} {score_text}:** {critique}")
            else:
                st.write(f"**Judge's Feedback:** {st.session_state.story_data.get('judge_critique', 'No feedback available.')}")
            st.write("**Themes:** Friendship, Courage, Whimsy")

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

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("↩️ Start Over at Desk", use_container_width=True):
            st.session_state.view = "desk"
            st.session_state.current_page = 0
            st.session_state.animation_mode = None
            st.session_state.story_data = {}
            st.session_state.pages = []
            st.session_state.page_images = {}
            st.rerun()
