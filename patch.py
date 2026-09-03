import re
with open("/home/nova/Desktop/RAG/app/retrieve.py", "r") as f:
    content = f.read()

orig_loop = """            # Modest Structural Signal
            # Boost structural chunks enough to be visible on vague queries
            for cid in list(fused_scores.keys()):
                chunk = self.chunks[cid]
                if chunk.get("is_structural", False):
                    fused_scores[cid] += 0.02"""

new_loop = """            # Modest Structural Signal
            # Boost structural chunks enough to be visible on vague queries (where they are the only matches)
            # but not enough to dominate specific queries (which score highly on both FAISS and BM25 natively).
            for cid in corpus_indices:
                chunk = self.chunks[cid]
                if chunk.get("is_structural", False):
                    if all_bm25_scores[cid] > 0 or cid in semantic_score_map:
                        if cid not in fused_scores:
                            fused_scores[cid] = 0.0
                        fused_scores[cid] += 0.02"""

content = content.replace(orig_loop, new_loop)
with open("/home/nova/Desktop/RAG/app/retrieve.py", "w") as f:
    f.write(content)
