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
        result = engine.run(user_input)
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

    print(result.outline.strip())

    print("=" * 60)
    print("Final Story")
    print("=" * 60)
    print(result.final_story.strip())

    if result.feedback:
        print("\n" + "-" * 60)
        print("Judge Feedback")
        print("-" * 60)
        print(f"Approved: {'Yes' if result.feedback.approved else 'No'}")
        print(f"Score   : {result.feedback.score}/10")
        if result.feedback.critique:
            print("Notes   :", result.feedback.critique)
    if result.image_prompt:
        print("\n" + "-" * 60)
        print("Illustration Prompt")
        print("-" * 60)
        print(result.image_prompt.strip())
    if getattr(result, "image_url", None):
        print("\nIllustration URL:", result.image_url)

    print("\n" + "=" * 60)
    print("All done. Sweet dreams! 🌙")
    print("=" * 60)


if __name__ == "__main__":
    main()