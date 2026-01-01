import os
from story_engine import StoryOrchestrator


def main():
    api_key = os.getenv("OPENAI_API_KEY") or input("Enter your OpenAI API key (or leave blank if set in env): ").strip()
    user_input = input("\nWhat kind of story do you want to hear? ")

    print("\n" + "=" * 60)
    print("Summoning the muses... ✨")
    print("=" * 60)
    print("→ Drafting...")
    engine = StoryOrchestrator(api_key=api_key if api_key else None)
    try:
        result = engine.run(user_input, genre="🐉 Adventure", length="medium")
    except Exception as exc:
        print("\n[ERROR] Story generation failed. Please verify your API key and try again.")
        print(f"Details: {exc}")
        return

    print(
        r"""
                       /$$     /$$ /$$
                      | $$    | $$|__/
  /$$$$$$  /$$   /$$ /$$$$$$  | $$ /$$ /$$$$$$$   /$$$$$$
 /$$__  $$| $$  | $$|_  $$_/  | $$| $$| $$__  $$ /$$__  $$
| $$  \ $$| $$  | $$  | $$    | $$| $$| $$  \ $$| $$$$$$$$
| $$  | $$| $$  | $$  | $$ /$$| $$| $$| $$  | $$| $$_____/
|  $$$$$$/|  $$$$$$/  |  $$$$/| $$| $$| $$  | $$|  $$$$$$$
 \______/  \______/    \___/  |__/|__/|__/  |__/ \_______/


"""
    )

    critiques = getattr(result, "feedback_history", None)
    if critiques:
        print("Judge Feedback")
        for idx, fb in enumerate(critiques, 1):
            status = "PASS ✅" if fb.approved else "REVISE"
            score_txt = f"score {fb.score}" if fb.score else "no score"
            critique_text = fb.critique.strip() or "PASS"
            print(f"[Round {idx}] ({status}, {score_txt}) {critique_text}")
    else:
        print(result.judge_critique.strip())

    print("=" * 60)
    print("Final Story")
    print("=" * 60)
    print(result.final_story.strip())

    if getattr(result, "image_url", None):
        print("\n" + "-" * 60)
        print("Illustration URL")
        print("-" * 60)
        print(result.image_url)

    print("\n" + "=" * 60)
    print("All done. Sweet dreams! 🌙")
    print("=" * 60)


if __name__ == "__main__":
    main()
