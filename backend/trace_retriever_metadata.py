import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.retrieve import Retriever
from app.config import INITIAL_GROUNDING_THRESHOLD
import pickle
from app.config import CHUNKS_V2_METADATA_PATH

def main():
    r = Retriever()
    topic = "SOLAR COLLECTORS:"
    filename = "BME654B-module-2-pdf.pdf"
    
    print(f"Total chunks in metadata: {r.total_chunks}")
    doc_chunks = [c for c in r.chunks if c.get("filename") == filename]
    print(f"Chunks for {filename}: {len(doc_chunks)}")
    
    if len(doc_chunks) > 0:
        print("Sample chunks for this document:")
        for c in doc_chunks[:5]:
            print(f" - ID: {c.get('chunk_id')}, Heading: {c.get('heading')}")

if __name__ == '__main__':
    main()
