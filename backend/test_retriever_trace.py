import asyncio
from app.retrieve import Retriever
import json

async def main():
    retriever = Retriever()
    retriever.load()
    
    print("Total chunks in retriever:", retriever.total_chunks)
    
    # Trace specific topic
    topic_specific = "GRID-TIED OR GRID-INTERACTIVE SYSTEMS:"
    chunks_specific = retriever.retrieve(topic_specific, top_k=5, filename="test.pdf")
    print(f"\n--- Specific Topic: {topic_specific} ---")
    print(f"Chunks retrieved: {len(chunks_specific)}")
    for i, c in enumerate(chunks_specific):
        print(f"  Chunk {i}: Score {c.get('score', 0):.4f} - {c.get('text', '')[:50]}...")
        
    # Trace All Topics
    topic_all = "All Topics"
    chunks_all = retriever.retrieve(topic_all, top_k=5, filename="test.pdf")
    print(f"\n--- All Topics: {topic_all} ---")
    print(f"Chunks retrieved: {len(chunks_all)}")
    for i, c in enumerate(chunks_all):
        print(f"  Chunk {i}: Score {c.get('score', 0):.4f} - {c.get('text', '')[:50]}...")

if __name__ == "__main__":
    asyncio.run(main())
