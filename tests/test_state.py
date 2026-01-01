import os
import pytest
from unittest.mock import patch, MagicMock
from app.state import ensure_state, get_api_key, set_api_key, DEFAULTS


class TestStateManagement:
    """Test state management functions."""
    
    @patch("app.state.st")
    def test_ensure_state_initializes_defaults(self, mock_st):
        """Test that ensure_state initializes all defaults."""
        mock_st.session_state = {}
        
        ensure_state()
        
        for key, val in DEFAULTS.items():
            assert key in mock_st.session_state
            assert mock_st.session_state[key] == val
    
    @patch("app.state.st")
    def test_ensure_state_preserves_existing(self, mock_st):
        """Test that ensure_state doesn't overwrite existing values."""
        mock_st.session_state = {"view": "book"}
        
        ensure_state()
        
        assert mock_st.session_state["view"] == "book"
        assert "current_page" in mock_st.session_state
    
    @patch("app.state.st")
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_from_session(self, mock_st):
        """Test getting API key from session state."""
        mock_st.session_state = {"user_api_key": "session-key"}
        
        key = get_api_key()
        
        assert key == "session-key"
    
    @patch("app.state.st")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"})
    def test_get_api_key_from_env(self, mock_st):
        """Test getting API key from environment."""
        mock_st.session_state = {}
        
        key = get_api_key()
        
        assert key == "env-key"
    
    @patch("app.state.st")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"})
    def test_get_api_key_session_priority(self, mock_st):
        """Test that session state takes priority over environment."""
        mock_st.session_state = {"user_api_key": "session-key"}
        
        key = get_api_key()
        
        assert key == "session-key"
    
    @patch("app.state.st")
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_empty(self, mock_st):
        """Test getting API key when none is set."""
        mock_st.session_state = {}
        
        key = get_api_key()
        
        assert key == ""
    
    @patch("app.state.st")
    def test_set_api_key(self, mock_st):
        """Test setting API key in session state."""
        mock_st.session_state = {}
        
        set_api_key("  new-key  ")
        
        assert mock_st.session_state["user_api_key"] == "new-key"
    
    @patch("app.state.st")
    def test_set_api_key_overwrites(self, mock_st):
        """Test that set_api_key overwrites existing key."""
        mock_st.session_state = {"user_api_key": "old-key"}
        
        set_api_key("new-key")
        
        assert mock_st.session_state["user_api_key"] == "new-key"
    
    @patch("app.state.st")
    def test_set_api_key_strips_whitespace(self, mock_st):
        """Test that set_api_key strips whitespace."""
        mock_st.session_state = {}
        
        set_api_key("  key with spaces  ")
        
        assert mock_st.session_state["user_api_key"] == "key with spaces"

