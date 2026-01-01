# Test Suite

This directory contains comprehensive tests for the Bedtime Storybook Agent application.

## Running Tests

From the project root directory:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_story_engine.py

# Run a specific test class
pytest tests/test_story_engine.py::TestStoryGenerator

# Run with coverage
pytest --cov=. --cov-report=html
```

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_story_engine.py` - Tests for core story generation logic (StoryGenerator, ImageGenerator, StoryOrchestrator)
- `test_helpers.py` - Tests for utility functions (text splitting, HTML escaping)
- `test_state.py` - Tests for state management functions
- `test_audio.py` - Tests for audio HTML generation
- `test_story_result.py` - Tests for StoryResult dataclass

## Test Coverage

The test suite covers:

- **Story Generation**: Story creation, judging, refinement, and image prompt generation
- **Image Generation**: DALL-E integration with error handling
- **Orchestration**: Full workflow with judge loop (PASS vs refinement paths)
- **Helper Functions**: Text pagination and HTML escaping
- **State Management**: Session state initialization and API key handling
- **Audio**: HTML/JavaScript generation for background music and narration

## Mocking

Tests use `unittest.mock` to mock OpenAI API calls, so tests can run without actual API keys or network access.

