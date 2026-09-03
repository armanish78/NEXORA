import sys
import os
import re
import pickle

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.retrieve import Retriever
from app.embeddings import embed_text
from app.vector_store import search_index

r = Retriever()

def trace_query(query, top_k=5, filename=None):
    print(f"\n{'='*80}\nTRACE FOR QUERY: '{query}' (filename={filename})\n{'='*80}")
    
    # 1. Active filename scope
    print(f"1. Active filename/document scope received by API/generator: {filename}")
    print(f"2. filename passed into Retriever.retrieve(): {filename}")

    # filter corpus
    if filename:
        corpus_indices = [i for i, c in enumerate(r.chunks) if c.get("filename") == filename]
        corpus_chunks = [r.chunks[i] for i in corpus_indices]
    else:
        corpus_indices = list(range(len(r.chunks)))
        corpus_chunks = r.chunks

    actual_top_k = min(top_k, len(corpus_chunks))
    deep_k = min(actual_top_k * 4, len(corpus_chunks))

    query_embedding = embed_text(r.model, query)

    # 3. FAISS candidates BEFORE filtering
    semantic_results_raw = search_index(r.index, r.chunks, query_embedding, top_k=min(deep_k * 2, r.total_chunks))
    print(f"\n3. FAISS candidates BEFORE document filtering (top {min(5, len(semantic_results_raw))}):")
    for res in semantic_results_raw[:5]:
        print(f"   [cid={res['chunk_id']}] file={res['filename']} score={res['score']:.4f}")

    # 4. BM25 candidates BEFORE filtering
    def tokenize(text):
        text = re.sub(r'[^\w\s]', '', text).lower()
        return text.split()

    tokenized_query = tokenize(query)
    all_bm25_scores = r.bm25.get_scores(tokenized_query) if r.bm25 else [0.0]*r.total_chunks
    bm25_raw = [(idx, all_bm25_scores[idx]) for idx in range(r.total_chunks) if all_bm25_scores[idx] > 0]
    bm25_raw.sort(key=lambda x: x[1], reverse=True)
    print(f"\n4. BM25 candidates BEFORE document filtering (top {min(5, len(bm25_raw))}):")
    for idx, score in bm25_raw[:5]:
        print(f"   [cid={idx}] file={r.chunks[idx].get('filename')} score={score:.4f}")

    # 5. Candidates AFTER document filtering
    semantic_results = [res for res in semantic_results_raw if filename is None or res.get("filename") == filename][:deep_k]
    semantic_score_map = {res["chunk_id"]: res["score"] for res in semantic_results}
    
    bm25_candidates = [(idx, all_bm25_scores[idx]) for idx in corpus_indices if all_bm25_scores[idx] > 0]
    bm25_candidates.sort(key=lambda x: x[1], reverse=True)
    bm25_top_indices = [idx for idx, _ in bm25_candidates[:deep_k]]

    print(f"\n5. Candidates AFTER document filtering:")
    print(f"   Semantic (top {len(semantic_results)}): {[c['chunk_id'] for c in semantic_results]}")
    print(f"   Lexical (top {len(bm25_top_indices)}): {bm25_top_indices}")

    # 6. RRF
    k_rrf = 60
    fused_scores = {}
    for res in semantic_results: fused_scores[res["chunk_id"]] = 0.0
    for idx in bm25_top_indices: fused_scores[idx] = 0.0
    
    for rank, res in enumerate(semantic_results):
        fused_scores[res["chunk_id"]] += (1.0 / (k_rrf + rank + 1))
    for rank, idx in enumerate(bm25_top_indices):
        fused_scores[idx] += (1.0 / (k_rrf + rank + 1))

    # Modest Structural Signal
    for cid in corpus_indices:
        chunk = r.chunks[cid]
        if chunk.get("is_structural", False):
            if all_bm25_scores[cid] > 0 or cid in semantic_score_map:
                if cid not in fused_scores:
                    fused_scores[cid] = 0.0
                fused_scores[cid] += 0.02

    ranked_cids = sorted(fused_scores.keys(), key=lambda cid: fused_scores[cid], reverse=True)
    print(f"\n6. RRF-ranked candidates (top 10):")
    for cid in ranked_cids[:10]:
        c = r.chunks[cid]
        print(f"   [cid={cid}] file={c.get('filename')} head={c.get('heading')} fused={fused_scores[cid]:.4f} struct={c.get('is_structural')}")

    # 7 & 8. Structural resolution
    print("\n7 & 8. Structural section-resolution result:")
    def tokenize_set(text):
        text = re.sub(r'[^\w\s]', '', text).lower()
        return set(text.split())
    query_tokens = tokenize_set(query)
    
    structural_target_headings = set()
    for cid in ranked_cids[:deep_k]:
        chunk = r.chunks[cid]
        if chunk.get("is_structural"):
            lines = chunk.get("text", "").split('\n')
            headings_in_chunk = [line.strip('- ').strip() for line in lines if line.strip().startswith('-')]
            best_heading = None
            best_score = 0
            for h in headings_in_chunk:
                h_tokens = tokenize_set(h)
                overlap = len(h_tokens.intersection(query_tokens))
                if overlap > best_score:
                    best_score = overlap
                    best_heading = h
            if best_heading and best_score > 0:
                structural_target_headings.add(best_heading)
                print(f"   Resolved structural chunk {cid} to heading: '{best_heading}' (score {best_score})")

    if structural_target_headings:
        for cid in corpus_indices:
            if r.chunks[cid].get("heading") in structural_target_headings:
                if cid not in fused_scores:
                    fused_scores[cid] = 0.0
                fused_scores[cid] += 0.01
                print(f"   Boosted cid {cid} under resolved heading '{r.chunks[cid].get('heading')}'")

    ranked_cids = sorted(fused_scores.keys(), key=lambda cid: fused_scores[cid], reverse=True)

    # 9. Final selected content chunks
    print("\n9. Final selected content chunks (before assembly, taking actual_top_k seeds):")
    for cid in ranked_cids[:actual_top_k]:
        print(f"   [cid={cid}] file={r.chunks[cid].get('filename')} head={r.chunks[cid].get('heading')} struct={r.chunks[cid].get('is_structural')}")

    # 10. Context assembled
    print("\n10. Context assembled for Qwen:")
    final_results = r.retrieve(query, top_k, filename)
    for res in final_results:
        print(f"   Result Rank {res.get('rank')}: [cid={res['chunk_id']}] file={res.get('filename')} struct={res.get('is_structural')} fused={res.get('fused_score'):.4f} len={len(res['text'])}")
        print(f"   Text preview: {res['text'][:100].replace(chr(10), ' ')}...")
        print(f"   Semantic={res.get('score'):.4f}, Lexical={res.get('lexical_score'):.4f}")

    # 11. Evidence / grounding
    print("\n11. Evidence/grounding signals and final decision:")
    from app.config import INITIAL_GROUNDING_THRESHOLD
    chunks = final_results
    program_match = re.search(r"\bprogram\s*[-]?\s*(\d+)\b", query, re.IGNORECASE)
    has_exact_program = False
    if program_match:
        program_number = program_match.group(1)
        program_pattern = re.compile(rf"\bPROGRAM\s*-\s*{re.escape(program_number)}\b", re.IGNORECASE)
        has_exact_program = any(
            program_pattern.search(chunk.get("text", "") + "\n" + str(chunk.get("heading", "")))
            for chunk in chunks
        )
    
    max_semantic = max((chunk.get("score", 0.0) for chunk in chunks), default=0.0)
    max_lexical = max((chunk.get("lexical_score", 0.0) for chunk in chunks), default=0.0)
    has_structural = any(chunk.get("is_structural", False) for chunk in chunks)
    
    is_grounded = False
    if max_semantic >= INITIAL_GROUNDING_THRESHOLD:
        is_grounded = True
    elif has_structural and max_lexical > 0:
        is_grounded = True
        
    final_decision = "ACCEPTED" if (is_grounded or has_exact_program) else "REJECTED"
    
    print(f"   has_exact_program: {has_exact_program}")
    print(f"   max_semantic: {max_semantic:.4f} (Threshold: {INITIAL_GROUNDING_THRESHOLD})")
    print(f"   max_lexical: {max_lexical:.4f}")
    print(f"   has_structural: {has_structural}")
    print(f"   FINAL DECISION: {final_decision}")

if __name__ == "__main__":
    trace_query("Explain program 4", top_k=5, filename=None)
    trace_query("What is this document about?", top_k=5, filename=None)
