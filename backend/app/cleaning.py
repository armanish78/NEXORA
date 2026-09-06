"""
app/cleaning.py
===============
Phase 5 — Text Cleaning

PURPOSE
-------
Provides deterministic, modular cleaning transformations for OCR and native
extracted text. The goal is to normalize artifacts (like hyphenated line
breaks or excessive whitespace) to improve the quality of chunks for embedding.

DESIGN PRINCIPLES
-----------------
1.  Conservative: Prioritize preservation of information. If a line break or
    character cannot be confidently classified as an artifact, keep it.
2.  Deterministic: No LLM usage here. Rules are regex or simple string ops.
3.  Modular: Each transformation is an independent function.
4.  Traceable: Does not overwrite raw ingestion files. Operates as a separate
    pipeline step.

RULES IMPLEMENTED
-----------------
- normalize_whitespace: Replaces 3+ newlines with 2. Removes trailing spaces.
- join_hyphenated_words: Joins words split across lines with a hyphen.
- join_paragraph_lines: Conservatively joins lines wrapped due to PDF margins.
- remove_page_headers: Removes known, repeated textbook headers/footers.

RULES REJECTED
--------------
- Aggressive spell correction: OCR errors in technical jargon could be "corrected"
  into unrelated common words.
- General "join all lines without periods": This would destroy equations, code
  blocks, lists, and headings.
"""

import re
import logging
from typing import List, Callable, Dict, Any

logger = logging.getLogger(__name__)


def normalize_whitespace(text: str) -> str:
    """
    Normalizes excessive whitespace.
    - Replaces 3 or more consecutive newlines with exactly 2 (paragraph break).
    - Removes trailing whitespace from each line.
    """
    if not text:
        return ""
    # Remove trailing spaces per line
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
    # Replace 3+ newlines with 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def join_hyphenated_words(text: str) -> str:
    """
    Joins words that were split across a line break with a hyphen.
    Example: "condi-\ntional" -> "conditional"
    
    Safe because it strictly requires alphabet characters on both sides
    of the hyphen and newline.
    """
    if not text:
        return ""
    # Match letters, a hyphen, optional spaces, a newline, optional spaces, and letters.
    return re.sub(r'([a-zA-Z]+)-[ \t]*\n[ \t]*([a-zA-Z]+)', r'\1\2', text)


def join_paragraph_lines(text: str) -> str:
    """
    Conservatively joins lines that appear to be wrapped paragraph text.
    
    Rule for joining Line 1 (L1) and Line 2 (L2):
    - L1 must end with a lowercase letter or a comma.
    - L2 must start with a lowercase letter.
    - L2 must NOT start with a common list marker (just as a safety check).
    
    Why conservative?
    - If L1 ends with a period, colon, or question mark, it's not joined.
    - If L2 starts with a capital letter (New sentence, Heading, Proper Noun),
      it's not joined. This misses some wraps (e.g. "into \nCohere") but
      guarantees we don't accidentally merge a heading into a paragraph or
      two bullet points together.
    """
    if not text:
        return ""
        
    lines = text.split('\n')
    out = []
    
    # Common list markers to avoid joining, even if other conditions match.
    list_marker = re.compile(r'^([•\-*]|\d+\.|[a-zA-Z]\))')
    
    for line in lines:
        if not out:
            out.append(line)
            continue
            
        prev = out[-1].rstrip()
        curr = line.lstrip()
        
        if not prev or not curr:
            out.append(line)
            continue
            
        # Check if prev ends with lowercase or comma
        if re.search(r'[a-z,]$', prev):
            # Check if curr starts with lowercase
            if re.match(r'^[a-z]', curr):
                if not list_marker.match(curr):
                    # Join with a space
                    out[-1] = prev + ' ' + curr
                    continue
                    
        out.append(line)
        
    return '\n'.join(out)


def remove_page_headers(text: str) -> str:
    """
    Removes known, repeated page headers and footers from the project documents.
    
    Textbook headers typically look like:
    - "Bayesian Learning « 235"
    - "236 « Machine Learning"
    
    Lab manual footers:
    - "Page 4"
    """
    if not text:
        return ""
        
    lines = text.split('\n')
    out = []
    
    for line in lines:
        stripped = line.strip()
        
        # Textbook headers
        if re.match(r'^Bayesian Learning « \d+$', stripped):
            continue
        if re.match(r'^\d+ « Machine Learning$', stripped):
            continue
            
        # Lab manual footer
        if re.match(r'^Page \d+$', stripped):
            continue
            
        # OKEN Scanner watermark from written notes
        if re.match(r'^\(?\d*\s*Scanned with OKEN Scanner\)?$', stripped, re.IGNORECASE):
            continue
            
        out.append(line)
        
    return '\n'.join(out)


def clean_text_pipeline(text: str, rules: List[Callable[[str], str]] = None) -> str:
    """
    Runs text through a sequence of cleaning rules.
    """
    if not text:
        return ""
        
    if rules is None:
        rules = [
            remove_page_headers,
            join_hyphenated_words,
            join_paragraph_lines,
            normalize_whitespace
        ]
        
    result = text
    for rule in rules:
        result = rule(result)
        
    return result


def clean_pages(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean every extracted page while preserving page number, source, 
    and any OCR metadata.
    """
    cleaned_pages = []

    for page in pages:
        # Create a shallow copy of the page dict to preserve metadata
        cleaned_page = dict(page)
        cleaned_page["text"] = clean_text_pipeline(page.get("text", ""))
        
        cleaned_pages.append(cleaned_page)

    return cleaned_pages