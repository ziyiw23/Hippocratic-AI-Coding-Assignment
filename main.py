from story_engine import StoryOrchestrator


def main():
    user_input = input("What kind of story do you want to hear? ")
    print("\n=== Summoning the muses... ===")
    print("-> Drafting outline...")
    engine = StoryOrchestrator()
    result = engine.run(user_input)

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

    print(
        r"""
 /$$$$$$$$ /$$                     /$$        /$$$$$$   /$$
| $$_____/|__/                    | $$       /$$__  $$ | $$
| $$       /$$ /$$$$$$$   /$$$$$$ | $$      | $$  \__//$$$$$$    /$$$$$$   /$$$$$$  /$$   /$$
| $$$$$   | $$| $$__  $$ |____  $$| $$      |  $$$$$$|_  $$_/   /$$__  $$ /$$__  $$| $$  | $$
| $$__/   | $$| $$  \ $$  /$$$$$$$| $$       \____  $$ | $$    | $$  \ $$| $$  \__/| $$  | $$
| $$      | $$| $$  | $$ /$$__  $$| $$       /$$  \ $$ | $$ /$$| $$  | $$| $$      | $$  | $$
| $$      | $$| $$  | $$|  $$$$$$$| $$      |  $$$$$$/ |  $$$$/|  $$$$$$/| $$      |  $$$$$$$
|__/      |__/|__/  |__/ \_______/|__/       \______/   \___/   \______/ |__/       \____  $$
                                                                                    /$$  | $$
                                                                                   |  $$$$$$/
                                                                                    \______/
"""
    )

    print(result.final_story.strip())

    if result.feedback:
        print("\n=== Judge Feedback ===")
        print(f"Approved: {result.feedback.approved}")
        print(f"Score   : {result.feedback.score}/10")
        if result.feedback.critique:
            print("Notes   :", result.feedback.critique)
    if result.image_prompt:
        print("\n=== Illustration Prompt ===")
        print(result.image_prompt.strip())
    if getattr(result, "image_url", None):
        print("\nIllustration URL:", result.image_url)

    print("\nAll done. Sweet dreams! 🌙")


if __name__ == "__main__":
    main()