import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.retrieve import Retriever
from app.config import INITIAL_GROUNDING_THRESHOLD

def main():
    r = Retriever()
    topic = "SOLAR COLLECTORS:"
    filename = "BME654B-module-2-pdf.pdf"
    
    print(f"INITIAL_GROUNDING_THRESHOLD: {INITIAL_GROUNDING_THRESHOLD}")
    chunks = r.retrieve(topic, top_k=5, filename=filename)
    
    print(f"Retrieved chunk count: {len(chunks)}")
    for i, c in enumerate(chunks):
        print(f"Rank {i+1}:")
        print(f"  Chunk ID: {c.get('chunk_id')}")
        print(f"  Filename: {c.get('filename')}")
        print(f"  Heading: {c.get('heading')}")
        print(f"  Is Structural: {c.get('is_structural')}")
        print(f"  Score (semantic): {c.get('score')}")
        print(f"  Fused Score: {c.get('fused_score')}")
        print(f"  Lexical Score: {c.get('lexical_score')}")
        print(f"  Text preview: {c.get('text', '')[:100].replace(chr(10), ' ')}")

if __name__ == '__main__':
    main()
