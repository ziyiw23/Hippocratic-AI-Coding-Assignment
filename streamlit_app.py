import os

import streamlit as st

from story_engine import StoryOrchestrator

st.set_page_config(page_title="Bedtime Story Builder", page_icon="🌙")
st.title("Bedtime Story Builder")

st.sidebar.header("Configuration")
api_key_input = st.sidebar.text_input("OpenAI API Key", type="password", help="Not stored.")
if api_key_input:
    os.environ["OPENAI_API_KEY"] = api_key_input

writer_temp = st.sidebar.slider("Creativity (writer temp)", 0.2, 1.0, 0.85, 0.05)
judge_temp = st.sidebar.slider("Strictness (judge temp)", 0.0, 0.4, 0.15, 0.01)
retries = st.sidebar.slider("Max refinement cycles", 0, 3, 2, 1)

prompt = st.text_area("What kind of story do you want?", height=180)
generate = st.button("Generate story")

if generate:
    if not prompt.strip():
        st.error("Please enter a story request.")
    elif not os.getenv("OPENAI_API_KEY"):
        st.error("Set OPENAI_API_KEY in your environment or sidebar.")
    else:
        engine = StoryOrchestrator(writer_temperature=writer_temp, judge_temperature=judge_temp)
        try:
            result = engine.run(prompt.strip(), retries=retries)
        except Exception as exc:
            st.error(f"Generation failed: {exc}")
        else:
            st.subheader("Outline")
            st.write(result.outline)

            st.subheader("Final story")
            st.write(result.final_story)

            st.subheader("Judge feedback")
            st.json(
                {
                    "approved": result.feedback.approved,
                    "score": result.feedback.score,
                    "critique": result.feedback.critique,
                    "iterations": result.iterations,
                }
            )

            st.subheader("Illustration prompt")
            st.write(result.image_prompt)

