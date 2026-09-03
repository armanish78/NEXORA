from app.retrieve import Retriever
retriever = Retriever()
results = retriever.retrieve("Explain program 4", top_k=5, filename="GenAI Lab manual.pdf")
print(f"Results len: {len(results)}")
for idx, r in enumerate(results):
    print(f"[{idx}] is_struct: {r.get('is_structural')} heading: {r.get('heading')} text_len: {len(r.get('text',''))}")
