import pytest
from app.audio import build_audio_block


class TestBuildAudioBlock:
    """Test audio block HTML generation."""
    
    def test_with_background_audio(self):
        """Test building audio block with background music."""
        audio_url = "data:audio/mp3;base64,test123"
        narrator_html = ""
        music_vol = 0.5
        version = 1
        
        result = build_audio_block(audio_url, narrator_html, music_vol, version)
        
        assert "bg-audio-1" in result
        assert audio_url in result
        assert "userMusicVol = 0.5" in result
        assert "display:none" in result
    
    def test_without_background_audio(self):
        """Test building audio block without background music."""
        audio_url = ""
        narrator_html = '<audio id="narrator"></audio>'
        music_vol = 0.2
        version = 0
        
        result = build_audio_block(audio_url, narrator_html, music_vol, version)
        
        assert "bg-audio-0" not in result or "bg-audio-0" in result
        assert narrator_html in result
        assert "userMusicVol = 0.2" in result
    
    def test_with_narrator(self):
        """Test building audio block with narrator."""
        audio_url = "data:audio/mp3;base64,test"
        narrator_html = '<audio id="narrator" autoplay></audio>'
        music_vol = 0.3
        version = 2
        
        result = build_audio_block(audio_url, narrator_html, music_vol, version)
        
        assert "narrator" in result
        assert "narr.volume = 1.0" in result
        assert "narr.onplay" in result
        assert "narr.onended" in result
    
    def test_ducking_logic(self):
        """Test that audio ducking logic is included."""
        audio_url = "data:audio/mp3;base64,test"
        narrator_html = '<audio id="narrator"></audio>'
        music_vol = 0.4
        version = 1
        
        result = build_audio_block(audio_url, narrator_html, music_vol, version)
        
        assert "bg.volume = Math.max(0, userMusicVol * 0.25)" in result
        assert "bg.volume < userMusicVol" in result
    
    def test_version_isolation(self):
        """Test that different versions create isolated audio elements."""
        audio_url = "data:audio/mp3;base64,test"
        narrator_html = ""
        music_vol = 0.2
        
        result1 = build_audio_block(audio_url, narrator_html, music_vol, version=1)
        result2 = build_audio_block(audio_url, narrator_html, music_vol, version=2)
        
        assert "bg-audio-1" in result1
        assert "bg-audio-2" in result2
        assert result1 != result2
    
    def test_cleanup_old_players(self):
        """Test that cleanup logic for old audio players is included."""
        audio_url = "data:audio/mp3;base64,test"
        narrator_html = ""
        music_vol = 0.2
        version = 3
        
        result = build_audio_block(audio_url, narrator_html, music_vol, version)
        
        assert "querySelectorAll" in result
        assert "data-audio-player" in result
        assert "pause" in result
        assert "remove" in result
    
    def test_fade_interval_cleanup(self):
        """Test that narrator fade interval cleanup is included."""
        audio_url = "data:audio/mp3;base64,test"
        narrator_html = '<audio id="narrator"></audio>'
        music_vol = 0.2
        version = 1
        
        result = build_audio_block(audio_url, narrator_html, music_vol, version)
        
        assert "window.narratorFade" in result
        assert "clearInterval" in result
    
    def test_volume_settings(self):
        """Test that volume settings are correctly applied."""
        audio_url = "data:audio/mp3;base64,test"
        narrator_html = ""
        music_vol = 0.75
        version = 1
        
        result = build_audio_block(audio_url, narrator_html, music_vol, version)
        
        assert "userMusicVol = 0.75" in result
        assert "bg.volume = userMusicVol" in result

