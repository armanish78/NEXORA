import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.vector_store import load_index
from app.config import FAISS_INDEX_PATH, CHUNKS_METADATA_PATH

def main():
    _, chunks, _ = load_index(FAISS_INDEX_PATH, CHUNKS_METADATA_PATH)
    doc_chunks = [c for c in chunks if c.get("filename") == "BME654B-module-2-pdf.pdf"]
    print(f"BME chunks in V1: {len(doc_chunks)}")
    
    for c in doc_chunks:
        if c.get("heading") == "SOLAR COLLECTORS:":
            print(f"Found match! Chunk text preview: {c.get('text', '')[:100]} | Score: N/A")

if __name__ == '__main__':
    main()
