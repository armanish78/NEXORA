import json
import os

os.makedirs('data/cleaned', exist_ok=True)

filler = " This is just a lot of extra text to ensure that this chunk is long enough to bypass the MINIMUM_CHUNK_SIZE threshold in chunk_pages. It needs to be at least 100 characters long to avoid being skipped. "

synthA = [
    {"page": 1, "filename": "Document A", "source": "Synthetic", "text": "Chapter 1\nThis is the first chapter about dogs." + filler * 5},
    {"page": 2, "filename": "Document A", "source": "Synthetic", "text": "Chapter 2\nThis is the second chapter about cats." + filler * 5},
    {"page": 3, "filename": "Document A", "source": "Synthetic", "text": "Chapter 3\nThis is the third chapter about birds." + filler * 5}
]

synthB = [
    {"page": 1, "filename": "Document B", "source": "Synthetic", "text": "1.1 Section A\nDetails of Section A." + filler * 5},
    {"page": 1, "filename": "Document B", "source": "Synthetic", "text": "1.2 Section B\nDetails of Section B." + filler * 5},
    {"page": 2, "filename": "Document B", "source": "Synthetic", "text": "1.3 Section C\nDetails of Section C." + filler * 5},
    {"page": 2, "filename": "Document B", "source": "Synthetic", "text": "1.4 Section D\nDetails of Section D." + filler * 5}
]

synthC = [
    {"page": 1, "filename": "Document C", "source": "Synthetic", "text": "MODULE 1 Title\nResearch on AI." + filler * 5},
    {"page": 1, "filename": "Document C", "source": "Synthetic", "text": "MODULE 2 Overview\nAn overview of AI." + filler * 5},
    {"page": 2, "filename": "Document C", "source": "Synthetic", "text": "MODULE 3 Methods\nWe used deep learning methods." + filler * 5},
    {"page": 3, "filename": "Document C", "source": "Synthetic", "text": "MODULE 4 Results\nThe results were positive." + filler * 5},
    {"page": 4, "filename": "Document C", "source": "Synthetic", "text": "MODULE 5 Conclusion\nIn conclusion, AI is good." + filler * 5}
]

with open('data/cleaned/synthA.json', 'w') as f:
    json.dump(synthA, f)
with open('data/cleaned/synthB.json', 'w') as f:
    json.dump(synthB, f)
with open('data/cleaned/synthC.json', 'w') as f:
    json.dump(synthC, f)

print("Synthetic documents created in data/cleaned/")
