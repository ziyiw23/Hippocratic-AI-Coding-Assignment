import pytest
from unittest.mock import MagicMock, patch

from story_engine import (
    StoryFeedback,
    StoryGenerator,
    StoryJudge,
    StoryOrchestrator,
)


class TestStoryGenerator:
    """Tests for StoryGenerator helpers."""

    @patch("story_engine.call_llm")
    def test_create_outline(self, mock_call, api_key):
        mock_call.return_value = "- intro"
        gen = StoryGenerator(api_key=api_key)

        outline = gen.create_outline("Tell me a tale", genre="🐉 Adventure", length="short")

        assert "- intro" in outline
        args = mock_call.call_args.kwargs
        assert args["temperature"] == 0.6
        assert "Genre/arc" in args["messages"][1]["content"]

    @patch("story_engine.call_llm")
    def test_write_story(self, mock_call, api_key):
        mock_call.return_value = "Final story"
        gen = StoryGenerator(writer_temperature=0.9, api_key=api_key)

        story = gen.write_story("Request", outline="- beats", genre="🧚 Fairy Tale", length="long")

        assert story == "Final story"
        args = mock_call.call_args.kwargs
        assert args["temperature"] == 0.9
        assert "🧚 Fairy Tale" in args["messages"][1]["content"]

    @patch("story_engine.call_llm")
    def test_refine_story(self, mock_call, api_key):
        mock_call.return_value = "Improved story"
        gen = StoryGenerator(api_key=api_key)

        refined = gen.refine_story("Draft", "Make it calmer")

        assert refined == "Improved story"
        assert "Rewrite the story" in mock_call.call_args.kwargs["messages"][1]["content"]

    @patch("story_engine.call_llm")
    def test_illustration_prompt(self, mock_call, api_key):
        mock_call.return_value = "Illustration prompt"
        gen = StoryGenerator(api_key=api_key)

        prompt = gen.illustration_prompt("Story")

        assert prompt == "Illustration prompt"
        assert mock_call.call_args.kwargs["max_tokens"] == 80


class TestStoryJudge:
    """Tests for StoryJudge behavior."""

    @patch("story_engine.call_llm")
    def test_evaluate_returns_feedback(self, mock_call, api_key):
        mock_call.return_value = '{"approved": true, "critique": "PASS", "score": 9}'
        judge = StoryJudge(api_key=api_key)

        feedback = judge.evaluate("Story")

        assert feedback.approved is True
        assert feedback.critique == "PASS"
        assert feedback.score == 9

    @patch("story_engine.call_llm")
    def test_evaluate_handles_invalid_json(self, mock_call, api_key):
        mock_call.return_value = "bad json"
        judge = StoryJudge(api_key=api_key)

        feedback = judge.evaluate("Story")

        assert feedback.approved is False
        assert "Invalid JSON" in feedback.critique
        assert feedback.score == 0


class TestStoryOrchestrator:
    """Tests for StoryOrchestrator run loop."""

    @patch("story_engine.ImageGenerator")
    @patch("story_engine.StoryJudge")
    @patch("story_engine.StoryGenerator")
    def test_run_collects_feedback_history(self, mock_gen_class, mock_judge_class, mock_image_class, api_key):
        mock_gen = MagicMock()
        mock_gen.create_outline.return_value = "Outline"
        mock_gen.write_story.return_value = "Draft"
        mock_gen.refine_story.return_value = "Refined"
        mock_gen.illustration_prompt.return_value = "Prompt"
        mock_gen_class.return_value = mock_gen

        feedback_fail = StoryFeedback(approved=False, critique="Needs softer tone", score=4)
        feedback_pass = StoryFeedback(approved=True, critique="PASS", score=9)
        mock_judge = MagicMock()
        mock_judge.evaluate.side_effect = [feedback_fail, feedback_pass]
        mock_judge_class.return_value = mock_judge

        mock_image = MagicMock()
        mock_image.generate_image.return_value = "https://example.com/img.png"
        mock_image_class.return_value = mock_image

        orch = StoryOrchestrator(api_key=api_key)
        result = orch.run("Request", genre="🐉 Adventure", length="medium", retries=2)

        assert result.final_story == "Refined"
        assert result.feedback_history == [feedback_fail, feedback_pass]
        assert result.iterations == 1
        mock_gen.refine_story.assert_called_once_with("Draft", "Needs softer tone")
        assert result.judge_critique == "PASS"

    @patch("story_engine.ImageGenerator")
    @patch("story_engine.StoryJudge")
    @patch("story_engine.StoryGenerator")
    def test_run_respects_retry_limit(self, mock_gen_class, mock_judge_class, mock_image_class, api_key):
        mock_gen = MagicMock()
        mock_gen.create_outline.return_value = "Outline"
        mock_gen.write_story.return_value = "Draft"
        mock_gen.refine_story.side_effect = ["Draft-1", "Draft-2"]
        mock_gen.illustration_prompt.return_value = "Prompt"
        mock_gen_class.return_value = mock_gen

        failing_feedback = StoryFeedback(approved=False, critique="Try again", score=2)
        mock_judge = MagicMock()
        mock_judge.evaluate.side_effect = [failing_feedback, failing_feedback, failing_feedback]
        mock_judge_class.return_value = mock_judge

        mock_image = MagicMock()
        mock_image.generate_image.return_value = None
        mock_image_class.return_value = mock_image

        orch = StoryOrchestrator(api_key=api_key)
        result = orch.run("Request", retries=1)

        assert len(result.feedback_history) == 2  # initial + one retry
        assert result.iterations == 1
        assert result.final_story == "Draft-1"
        assert result.image_url is None
