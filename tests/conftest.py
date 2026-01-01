import os
import pytest
from unittest.mock import Mock, MagicMock, patch


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = MagicMock()
    
    # Mock chat completion response
    mock_chat_response = MagicMock()
    mock_chat_response.choices = [MagicMock()]
    mock_chat_response.choices[0].message.content = "Once upon a time..."
    
    # Mock image generation response
    mock_image_response = MagicMock()
    mock_image_response.data = [MagicMock()]
    mock_image_response.data[0].url = "https://example.com/image.png"
    
    mock_client.chat.completions.create.return_value = mock_chat_response
    mock_client.images.generate.return_value = mock_image_response
    
    return mock_client


@pytest.fixture
def mock_streamlit_session_state():
    """Mock Streamlit session state."""
    return {}


@pytest.fixture
def sample_story():
    """Sample story text for testing."""
    return """Once upon a time, in a magical forest, there lived a tiny dragon named Sparkle.

Sparkle was different from other dragons. Instead of breathing fire, Sparkle breathed bubbles of all colors.

One day, Sparkle decided to visit the nearby village and share the beautiful bubbles with the children.

The children were delighted and danced among the colorful bubbles, laughing with joy.

From that day on, Sparkle became the village's favorite friend, bringing happiness wherever they went."""


@pytest.fixture
def api_key():
    """Test API key."""
    return "test-api-key-12345"

