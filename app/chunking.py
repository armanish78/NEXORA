import re
from typing import List, Tuple, Dict, Any
from app.config import CHUNK_SIZE, CHUNK_OVERLAP, MINIMUM_CHUNK_SIZE

def is_heading(line: str) -> bool:
    """
    Conservatively checks if a line is likely a heading.
    """
    line = line.strip()
    if not line:
        return False
    
    if len(line) > 80: # Too long to be a normal heading
        return False
        
    # Pattern 1: Chapter / Module / Unit
    if re.match(r'^(?:MODULE|CHAPTER|UNIT)\s+\d+', line, re.IGNORECASE):
        return True
        
    # Pattern 2: Numbering like 1.2, 3.4.1
    if re.match(r'^\d+\.\d+(?:\.\d+)?\s+[A-Z]', line):
        return True
        
    # Pattern 3: All caps short line
    if line.isupper() and len(line) > 3:
        return True
        
    return False

def find_best_split(text: str, start: int, target_end: int) -> int:
    """
    Finds the best natural boundary to split the text between start and target_end.
    Returns the index in `text` where the split should occur.
    """
    candidate = text[start:target_end]
    
    # 1. Heading (split before heading)
    paragraph_breaks = list(re.finditer(r'\n[ \t]*\n', candidate))
    if paragraph_breaks:
        for match in reversed(paragraph_breaks):
            idx = match.end()
            next_newline = candidate.find('\n', idx)
            if next_newline == -1:
                next_newline = len(candidate)
            line = candidate[idx:next_newline]
            if is_heading(line):
                return start + match.start()
                
    # 2. Paragraph boundary (\n\n)
    if paragraph_breaks:
        return start + paragraph_breaks[-1].start()
        
    # 3. Single newline (\n)
    newline_breaks = list(re.finditer(r'\n', candidate))
    if newline_breaks:
        return start + newline_breaks[-1].start()
        
    # 4. Sentence boundary
    sentence_breaks = list(re.finditer(r'[.!?](?:\s+|$)', candidate))
    if sentence_breaks:
        return start + sentence_breaks[-1].end()
        
    # 5. Word boundary
    space_pos = candidate.rfind(' ')
    if space_pos != -1:
        return start + space_pos + 1
        
    return target_end

def chunk_text_structural(text: str, chunk_size: int, overlap: int) -> List[Tuple[str, int, int]]:
    """
    Splits text into structure-aware chunks.
    Returns a list of tuples: (chunk_text, start_index, end_index)
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")
        
    chunks = []
    text_length = len(text)
    start = 0
    
    while start < text_length:
        while start < text_length and text[start].isspace():
            start += 1
            
        if start >= text_length:
            break
            
        target_end = min(start + chunk_size, text_length)
        
        if target_end == text_length:
            end = text_length
        else:
            end = find_best_split(text, start, target_end)
            if end <= start:
                end = target_end
                
        chunk = text[start:end].strip()
        if chunk:
            chunks.append((chunk, start, end))
            
        if end == text_length:
            break
            
        if overlap > 0:
            next_start = end - overlap
            if next_start <= start:
                next_start = end
            start = next_start
        else:
            start = end
            
    return chunks

def chunk_pages(pages: List[Dict[str, Any]], chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP, minimum_chunk_size=MINIMUM_CHUNK_SIZE) -> List[Dict[str, Any]]:
    """
    Convert cleaned pages into structured chunks across page boundaries.
    Preserves document structure as metadata (headings, hierarchy).
    """
    if not pages:
        return []
        
    filename = pages[0].get("filename", "unknown")
    source = pages[0].get("source", "unknown")
    
    full_text = ""
    page_boundaries = []
    
    current_idx = 0
    for page in pages:
        text = page.get("text", "").strip()
        if not text:
            continue
        page_num = page.get("page", 0)
        
        added_text = text + "\n\n"
        full_text += added_text
        
        start_idx = current_idx
        current_idx += len(added_text)
        end_idx = current_idx
        
        page_boundaries.append((start_idx, end_idx, page_num))
        
    raw_chunks = chunk_text_structural(full_text, chunk_size, overlap)
    
    chunks = []
    current_heading = None
    headings_list = []
    
    for chunk_idx, (chunk_text_val, c_start, c_end) in enumerate(raw_chunks):
        if len(chunk_text_val) < minimum_chunk_size:
            continue
            
        covered_pages = []
        for p_start, p_end, p_num in page_boundaries:
            if c_start < p_end and c_end > p_start:
                if p_num not in covered_pages:
                    covered_pages.append(p_num)
                    
        if len(covered_pages) == 1:
            page_field = covered_pages[0]
        else:
            page_field = covered_pages

        # Check for headings in this chunk to update current_heading
        lines = chunk_text_val.split('\n')
        for line in lines:
            if is_heading(line):
                current_heading = line.strip()
                if current_heading not in headings_list:
                    headings_list.append(current_heading)
            
        chunks.append({
            "chunk_id": len(chunks),
            "text": chunk_text_val,
            "page": page_field,
            "source": source,
            "filename": filename,
            "heading": current_heading,
            "is_structural": False
        })
        
    # Generate small structural index chunks (batching headings into chunks of ~10 headings)
    if headings_list:
        batch_size = 10
        for i in range(0, len(headings_list), batch_size):
            batch = headings_list[i:i+batch_size]
            outline_text = f"DOCUMENT STRUCTURE SECTION for {filename} (Overview, Summary, Table of Contents, Chapters, Sections, Parts):\n" + "\n".join(f"- {h}" for h in batch)
            chunks.append({
                "chunk_id": len(chunks),
                "text": outline_text,
                "page": "Metadata",
                "source": source,
                "filename": filename,
                "heading": "Document Outline",
                "is_structural": True
            })

    return chunks