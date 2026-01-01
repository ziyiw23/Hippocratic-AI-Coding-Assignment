from story_engine import StoryOrchestrator


def main():
    user_input = input("What kind of story do you want to hear? ")
    engine = StoryOrchestrator()
    result = engine.run(user_input)
    print("\nOutline:\n")
    print(result.outline)
    print("\nFinal story:\n")
    print(result.final_story)
    if result.feedback:
        print("\nJudge feedback:")
        print(f"Approved: {result.feedback.approved}, Score: {result.feedback.score}")
        print(result.feedback.critique)
    if result.image_prompt:
        print("\nIllustration prompt:")
        print(result.image_prompt)


if __name__ == "__main__":
    main()