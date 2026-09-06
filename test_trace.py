import sys
import os

# Append the current directory to sys.path
sys.path.append(os.path.abspath("backend"))

os.chdir("backend")

from app.retrieve import Retriever
from app.quiz_generator import get_difficulty_strategy
from app.config import INITIAL_GROUNDING_THRESHOLD

retriever = Retriever()

topic = "SOLAR COLLECTORS:"
filename = "BME654B-module-2-pdf.pdf"
difficulty = "medium"

strategy = get_difficulty_strategy(difficulty)
top_k = strategy.get_num_chunks()

print(f"1. Filename reaching generator: {filename}")
print(f"2. Topic reaching generator: {topic}")
print(f"3. Arguments to retriever (if called): topic='{topic}', top_k={top_k}, filename='{filename}'")

chunks = []

from app.vector_store import load_index
_, v1_chunks, _ = load_index()
doc_chunks = [c for c in v1_chunks if c.get("filename") == filename]
exact_chunks = [c for c in doc_chunks if c.get("heading") == topic]
print(f"Found {len(exact_chunks)} exact chunks for structural match.")

if not exact_chunks:
    print("Falling back to Retriever...")
    chunks = retriever.retrieve(topic, top_k=top_k, filename=filename)
    print(f"4. How many chunks are returned? {len(chunks)}")
    print(f"5. Top 5 scores & 6. Filenames/headings:")
    for i, c in enumerate(chunks[:5]):
        print(f"   [{i}] Score: {c.get('score')} | Heading: {c.get('heading')} | Filename: {c.get('filename')}")
    
    if chunks:
        print(f"7. Does grounding gate reject them?")
        if chunks[0].get("score", 0) < INITIAL_GROUNDING_THRESHOLD:
            print(f"   Yes, score {chunks[0].get('score', 0)} < {INITIAL_GROUNDING_THRESHOLD}")
            print(f"8. If yes, why exactly? (Score too low)")
        else:
            print("   No, grounding gate passes based on score.")
