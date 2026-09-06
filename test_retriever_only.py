import sys
import os

sys.path.append(os.path.abspath("backend"))
os.chdir("backend")

from app.retrieve import Retriever
retriever = Retriever()
topic = "SOLAR COLLECTORS:"
filename = "BME654B-module-2-pdf.pdf"
chunks = retriever.retrieve(topic, top_k=2, filename=filename)
print(f"4. How many chunks returned? {len(chunks)}")
print("5 & 6:")
for i, c in enumerate(chunks[:5]):
    print(f"[{i}] Score: {c.get('score')} | Heading: {c.get('heading')} | File: {c.get('filename')}")
