import json
from app.retrieve import Retriever
import re

retriever = Retriever()

query = "What are the important things I should study from this?"
filename = "BME654B-module-2-pdf.pdf"
top_k = 5

# 1. intent
def tokenize_set(text):
    text = re.sub(r'[^\w\s]', '', text).lower()
    return set(text.split())

intent = "DOCUMENT_WIDE"

# 2. corpus indices
corpus_indices = [i for i, c in enumerate(retriever.chunks) if c.get("filename") == filename]
corpus_chunks = [retriever.chunks[i] for i in corpus_indices]

actual_top_k = min(top_k, len(corpus_chunks))
deep_k = min(actual_top_k * 4, len(corpus_chunks))

# 3. FAISS
from app.vector_store import search_index
import numpy as np
from app.embeddings import embed_text, load_embedding_model

model = load_embedding_model()
query_embedding = embed_text(model, query)
semantic_results_raw = search_index(retriever.index, retriever.chunks, query_embedding, top_k=len(retriever.chunks))
semantic_results = [r for r in semantic_results_raw if r.get("filename") == filename][:deep_k]

# 4. BM25
tokenized_query = query.split()
bm25_scores = retriever.bm25.get_scores(tokenized_query)
bm25_doc_scores = [(i, bm25_scores[i]) for i in corpus_indices]
bm25_doc_scores.sort(key=lambda x: x[1], reverse=True)
bm25_top_indices = [idx for idx, score in bm25_doc_scores[:deep_k] if score > 0]
all_bm25_scores = {i: 0.0 for i in range(len(retriever.chunks))}
for i, s in zip(corpus_indices, [bm25_scores[i] for i in corpus_indices]):
    all_bm25_scores[i] = s

# 5. RRF
fused_scores = {}
for rank, res in enumerate(semantic_results):
    cid = res["chunk_id"]
    if cid not in fused_scores:
        fused_scores[cid] = 0.0
    fused_scores[cid] += 1.0 / (60 + rank + 1)

for rank, idx in enumerate(bm25_top_indices):
    if idx not in fused_scores:
        fused_scores[idx] = 0.0
    fused_scores[idx] += 1.0 / (60 + rank + 1)

# Structural resolution
query_tokens = tokenize_set(query)
ranked_cids = sorted(fused_scores.keys(), key=lambda cid: fused_scores[cid], reverse=True)[:actual_top_k]

structural_target_headings = {}
for cid in ranked_cids[:deep_k]:
    chunk = retriever.chunks[cid]
    if chunk.get("is_structural"):
        lines = chunk.get("text", "").split('\n')
        headings = [line.strip('- ').strip() for line in lines if line.strip().startswith('-')]
        best_heading = None
        best_score = 0
        for h in headings:
            overlap = len(tokenize_set(h).intersection(query_tokens))
            if overlap > best_score:
                best_score = overlap
                best_heading = h
        if best_heading and best_score > 0:
            current = structural_target_headings.get(best_heading, 0.0)
            structural_target_headings[best_heading] = max(current, fused_scores[cid])

if structural_target_headings:
    for cid in corpus_indices:
        heading = retriever.chunks[cid].get("heading")
        if heading in structural_target_headings:
            if cid not in fused_scores:
                fused_scores[cid] = 0.0
            fused_scores[cid] += (structural_target_headings[heading] + 0.001)

ranked_cids = sorted(fused_scores.keys(), key=lambda cid: fused_scores[cid], reverse=True)

# 6. DUMP
print(f"--- CANDIDATE RANKING BEFORE DIVERSITY (Top 20) ---")
for i, cid in enumerate(ranked_cids[:20]):
    chunk = retriever.chunks[cid]
    struct = "STRUCT" if chunk.get("is_structural") else "NORMAL"
    print(f"Rank {i+1}: Chunk {cid} | {struct} | Score: {fused_scores[cid]:.5f} | Heading: {chunk.get('heading')}")

print(f"\n--- STRUCTURAL CHUNKS IN DOCUMENT ---")
for cid in corpus_indices:
    chunk = retriever.chunks[cid]
    if chunk.get("is_structural"):
        print(f"Chunk {cid} | Heading: {chunk.get('heading')} | Score in fused_scores: {fused_scores.get(cid, 0.0):.5f}")

