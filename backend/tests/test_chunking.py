import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.chunking import chunk_text_structural, chunk_pages, is_heading

class TestIsHeading:
    def test_chapter_module(self):
        assert is_heading("MODULE 1")
        assert is_heading("Chapter 4")
        assert is_heading("UNIT 2")

    def test_numbering_pattern(self):
        assert is_heading("1.2 Introduction")
        assert is_heading("10.3.1 Summary")
        
    def test_all_caps(self):
        assert is_heading("CONCLUSION")
        assert not is_heading("YES") # too short
        
    def test_normal_text(self):
        assert not is_heading("This is just a normal sentence.")
        
    def test_long_line(self):
        assert not is_heading("A VERY LONG LINE THAT HAPPENS TO BE IN CAPS BUT IT IS DEFINITELY TOO LONG TO BE A HEADING BECAUSE IT EXCEEDS EIGHTY CHARACTERS WHICH IS A LOT")

class TestChunkTextStructural:
    def test_heading_split(self):
        text = "Some intro text.\n\nMODULE 1\nHere is the content for module 1."
        chunks = chunk_text_structural(text, 35, 0)
        assert chunks[0][0] == "Some intro text."
        assert chunks[1][0] == "MODULE 1"
        
    def test_paragraph_split(self):
        text = "Paragraph 1 is here.\n\nParagraph 2 is here."
        chunks = chunk_text_structural(text, 30, 0)
        assert chunks[0][0] == "Paragraph 1 is here."
        assert chunks[1][0] == "Paragraph 2 is here."
        
    def test_single_newline_split(self):
        text = "List:\n- Item 1\n- Item 2"
        chunks = chunk_text_structural(text, 15, 0)
        assert chunks[0][0] == "List:\n- Item 1"
        assert chunks[1][0] == "- Item 2"
        
    def test_sentence_split(self):
        text = "This is a long sentence. This is another sentence."
        chunks = chunk_text_structural(text, 35, 0)
        assert chunks[0][0] == "This is a long sentence."
        assert chunks[1][0] == "This is another sentence."
        
    def test_word_split(self):
        text = "word1 word2 word3 word4"
        chunks = chunk_text_structural(text, 12, 0)
        assert chunks[0][0] == "word1 word2"
        assert chunks[1][0] == "word3 word4"
        
    def test_hard_split(self):
        text = "a"*100
        chunks = chunk_text_structural(text, 30, 0)
        assert len(chunks) == 4
        assert len(chunks[0][0]) == 30
        
class TestChunkPages:
    def test_cross_page_boundaries(self):
        pages = [
            {"filename": "test.pdf", "page": 1, "text": "Part 1 of the", "source": "text"},
            {"filename": "test.pdf", "page": 2, "text": "sentence.", "source": "text"}
        ]
        # Text becomes "Part 1 of the\n\nsentence.\n\n"
        chunks = chunk_pages(pages, chunk_size=100, overlap=0, minimum_chunk_size=5)
        assert len(chunks) == 1
        assert chunks[0]["page"] == [1, 2]
        assert chunks[0]["text"] == "Part 1 of the\n\nsentence."
        
    def test_maintains_metadata(self):
        pages = [
            {"filename": "test.pdf", "page": 1, "text": "Hello world", "source": "ocr"}
        ]
        chunks = chunk_pages(pages, chunk_size=50, overlap=0, minimum_chunk_size=5)
        assert chunks[0]["filename"] == "test.pdf"
        assert chunks[0]["source"] == "ocr"
        assert chunks[0]["page"] == 1
        assert chunks[0]["chunk_id"] == 0
