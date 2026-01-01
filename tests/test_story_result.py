import pytest

from story_engine import StoryFeedback, StoryResult


def _make_result(feedback_history):
    final_feedback = feedback_history[-1]
    return StoryResult(
        request="Make a story",
        outline="- intro\n- middle\n- ending",
        draft="Draft story",
        final_story="Final story",
        feedback=final_feedback,
        image_prompt="Prompt",
        image_url="https://example.com/image.png",
        iterations=len(feedback_history) - 1,
        feedback_history=feedback_history,
    )


class TestStoryResult:
    """Tests for StoryResult enrichment helpers."""

    def test_judge_properties(self):
        feedback_history = [
            StoryFeedback(approved=False, critique="Needs simpler words", score=4),
            StoryFeedback(approved=True, critique="PASS", score=10),
        ]

        result = _make_result(feedback_history)

        assert result.judge_critique == "PASS"
        assert result.judge_critiques == ["Needs simpler words", "PASS"]
        assert result.iterations == 1

    def test_missing_feedback_history_defaults(self):
        feedback = StoryFeedback(approved=True, critique="PASS", score=10)
        result = StoryResult(
            request="Request",
            outline="Outline",
            draft="Draft",
            final_story="Story",
            feedback=feedback,
            image_prompt="Prompt",
            image_url=None,
            iterations=0,
        )
        assert result.judge_critique == "PASS"
        assert result.judge_critiques == []

    def test_all_fields_required(self):
        feedback = StoryFeedback(approved=True, critique="PASS", score=10)
        with pytest.raises(TypeError):
            StoryResult(
                request="Req",
                outline="Outline",
                draft="Draft",
                final_story="Story",
                feedback=feedback,
                image_prompt="Prompt",
            )
