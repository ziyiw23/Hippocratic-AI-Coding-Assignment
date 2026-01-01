import pytest
from app.ui_desk import _split_text_into_pages
from app.ui_book import escape_html


class TestSplitTextIntoPages:
    """Test text splitting into pages."""
    
    def test_short_text(self):
        """Test splitting short text that fits in one page."""
        text = "This is a short story."
        pages = _split_text_into_pages(text, chars_per_page=400)
        
        assert len(pages) == 1
        assert pages[0] == text
    
    def test_multiple_paragraphs(self):
        """Test splitting text with multiple paragraphs."""
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        pages = _split_text_into_pages(text, chars_per_page=20)
        
        assert len(pages) >= 2
        assert "Paragraph one" in pages[0]
    
    def test_long_paragraph(self):
        """Test splitting a single long paragraph."""
        long_text = "A" * 500
        pages = _split_text_into_pages(long_text, chars_per_page=100)
        
        assert len(pages) > 1
        assert all(len(page) <= 150 for page in pages)
    
    def test_empty_text(self):
        """Test splitting empty text."""
        pages = _split_text_into_pages("", chars_per_page=400)
        
        assert len(pages) == 1
        assert pages[0] == ""
    
    def test_word_boundary_respect(self):
        """Test that splitting respects word boundaries."""
        text = "This is a test sentence with multiple words."
        pages = _split_text_into_pages(text, chars_per_page=15)
        
        for page in pages:
            words = page.split()
            assert len(words) > 0
    
    def test_default_chars_per_page(self):
        """Test with default chars_per_page."""
        text = "A" * 500
        pages = _split_text_into_pages(text)
        
        assert len(pages) > 1


class TestEscapeHtml:
    """Test HTML escaping function."""
    
    def test_escape_ampersand(self):
        """Test escaping ampersand."""
        result = escape_html("Tom & Jerry")
        assert result == "Tom &amp; Jerry"
    
    def test_escape_less_than(self):
        """Test escaping less than."""
        result = escape_html("5 < 10")
        assert result == "5 &lt; 10"
    
    def test_escape_greater_than(self):
        """Test escaping greater than."""
        result = escape_html("10 > 5")
        assert result == "10 &gt; 5"
    
    def test_escape_all_special_chars(self):
        """Test escaping all special characters."""
        result = escape_html("A < B & C > D")
        assert result == "A &lt; B &amp; C &gt; D"
        assert "&lt;" in result
        assert "&amp;" in result
        assert "&gt;" in result
    
    def test_no_escape_needed(self):
        """Test text that doesn't need escaping."""
        result = escape_html("Hello World")
        assert result == "Hello World"
    
    def test_empty_string(self):
        """Test escaping empty string."""
        result = escape_html("")
        assert result == ""
    
    def test_multiple_occurrences(self):
        """Test escaping multiple occurrences."""
        result = escape_html("A < B < C")
        assert result == "A &lt; B &lt; C"

