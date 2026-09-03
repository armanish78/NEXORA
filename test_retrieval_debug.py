from app.retrieve import Retriever
r = Retriever()
results = r.retrieve("how many total programs", top_k=10, filename="GenAI Lab manual.pdf")
print("RESULTS FOR 'how many total programs'")
for i, x in enumerate(results):
    print(f"[{i}] id:{x['chunk_id']} struct:{x.get('is_structural')} score:{x['fused_score']:.4f} text:{x['text'][:50]}")
