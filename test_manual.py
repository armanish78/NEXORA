from app.retrieve import Retriever

r = Retriever()
print("Total chunks:", r.total_chunks)
print("Is BM25 loaded:", hasattr(r, "bm25") and r.bm25 is not None)

for c in r.chunks:
    if c.get("is_structural"):
        print(f"STRUCT CHUNK {c['chunk_id']} file={c.get('filename')}: {repr(c.get('text'))}")

for doc, query in [
    ("Document A", "How many chapters are there in Document A?"),
    ("Document B", "What sections are included in Document B?"),
    ("Document C", "Where are the results discussed in Document C?"),
    ("GenAI", "how many total programs")
]:
    print(f"\nQUERY: {query}")
    results = r.retrieve(query, top_k=5)
    for res in results:
        print(f"[{res.get('rank')}] [{res.get('chunk_id')}] file={res.get('filename')} struct={res.get('is_structural')} score={res.get('score', 0):.3f} fused={res.get('fused_score', 0):.3f} bm25={res.get('lexical_score', 0):.3f}")
        print("    ", repr(res.get("text", "")[:100]))
