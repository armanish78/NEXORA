import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.retrieve import Retriever
from app.config import FAISS_INDEX_PATH, CHUNKS_METADATA_PATH

def main():
    r_v1 = Retriever(index_path=FAISS_INDEX_PATH, metadata_path=CHUNKS_METADATA_PATH)
    topic = "SOLAR COLLECTORS:"
    filename = "BME654B-module-2-pdf.pdf"
    
    chunks = r_v1.retrieve(topic, top_k=5, filename=filename)
    print(f"Retrieved {len(chunks)} from V1 index")
    for i, c in enumerate(chunks):
        print(f"Rank {i+1}:")
        print(f"  Chunk ID: {c.get('chunk_id')}")
        print(f"  Heading: {c.get('heading')}")
        print(f"  Score: {c.get('score')}")
        print(f"  Fused Score: {c.get('fused_score')}")

if __name__ == '__main__':
    main()
