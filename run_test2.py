from app.retrieve import Retriever
retriever = Retriever()
filename = "GenAI Lab manual.pdf"
corpus_indices = [i for i, c in enumerate(retriever.chunks) if c.get("filename") == filename]
print(f"Corpus chunks: {len(corpus_indices)}")
