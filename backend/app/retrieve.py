import time
import re
import os
import pickle
from typing import List, Dict, Any

from app.embeddings import load_embedding_model, embed_text
from app.vector_store import load_index, search_index
from app.config import FAISS_V2_INDEX_PATH, CHUNKS_V2_METADATA_PATH


class Retriever:
    """
    Stateful retrieval component.

    Loads the embedding model and FAISS index once.

    Explicit "Program N" queries:
    - Find the exact PROGRAM N heading.
    - Retrieve the surrounding chunks belonging to that program.
    - Keep the exact program context together.

    Normal queries:
    - Use standard FAISS semantic retrieval.
    """

    def __init__(
        self,
        index_path: str = FAISS_V2_INDEX_PATH,
        metadata_path: str = CHUNKS_V2_METADATA_PATH
    ):
        self.index_path = index_path
        self.metadata_path = metadata_path

        if not os.path.exists(self.index_path) or not os.path.exists(
            self.metadata_path
        ):
            raise FileNotFoundError(
                "FAISS index or metadata not found. "
                "Please run the indexing pipeline first."
            )

        self.model = load_embedding_model()

        from app.config import BM25_V2_INDEX_PATH
        self.index, self.chunks, self.bm25 = load_index(
            self.index_path,
            self.metadata_path,
            BM25_V2_INDEX_PATH
        )

        self.total_chunks = len(self.chunks)

    def _find_program_chunks(
        self,
        program_number: str,
        query_results: List[Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Find the exact Program heading and collect nearby chunks.

        The heading itself identifies where the program starts.
        We then include subsequent chunks so that code/examples
        belonging to that program are available to the generator.
        """

        pattern = re.compile(
            rf"\bPROGRAM\s*-\s*{re.escape(program_number)}\b",
            re.IGNORECASE
        )

        heading_chunk_id = None
        heading_result = None

        # ------------------------------------------------------------
        # Find exact program heading
        # ------------------------------------------------------------

        for result in query_results:
            text = result.get("text", "")

            if pattern.search(text):
                heading_chunk_id = result["chunk_id"]
                heading_result = result
                break

        if heading_chunk_id is None:
            return []

        # ------------------------------------------------------------
        # Determine the program's chunk range
        # ------------------------------------------------------------

        start_id = heading_chunk_id

        # Find the next PROGRAM heading.
        next_program_id = self.total_chunks

        generic_program_pattern = re.compile(
            r"\bPROGRAM\s*-\s*\d+\b",
            re.IGNORECASE
        )

        for chunk in self.chunks:
            cid = chunk["chunk_id"]

            if cid <= start_id:
                continue

            if generic_program_pattern.search(
                chunk.get("text", "")
            ):
                next_program_id = cid
                break

        # ------------------------------------------------------------
        # Collect chunks belonging to this program.
        #
        # Limit the amount of context to avoid flooding Qwen.
        # ------------------------------------------------------------

        program_chunks = []


        return program_chunks[:max_program_chunks]

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filename: str = None
    ) -> List[Dict[str, Any]]:

        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty or whitespace."
            )

        def classify_query_intent(q: str) -> str:
            clean_q = re.sub(r'[^\w\s]', '', q.lower())
            tokens = set(clean_q.split())
            
            generic_words = {
                "what", "is", "the", "a", "an", "this", "document", "module", "paper", "text", "here", 
                "of", "in", "to", "for", "with", "on", "at", "from", "by", "about", 
                "are", "should", "i", "you", "me", "we", "they", "it", "can", "tell", "explain", "describe",
                "study", "learn", "focus", "understand", "important", "main", "key", "things", "ideas", "topics", "points",
                "summary", "overview", "big", "picture", "break", "down", "walk", "through", "everything", "all", "detail",
                "does", "say", "do", "how", "why", "when", "who", "where", "which"
            }
            
            broad_modifiers = {
                "overview", "summary", "everything", "all", "important", "main", "key", 
                "focus", "ideas", "topics", "points", "picture", "understand", "learn", "study", "about"
            }
            
            doc_refs = {"document", "module", "paper", "text", "here", "this"}
            
            specific_content_words = tokens - generic_words
            has_broad_modifier = len(tokens.intersection(broad_modifiers)) > 0
            has_doc_ref = len(tokens.intersection(doc_refs)) > 0
            
            if len(tokens) <= 4 and has_doc_ref and len(specific_content_words) == 0:
                return "DOCUMENT_WIDE"
                
            if has_broad_modifier or has_doc_ref:
                if len(specific_content_words) <= 1:
                    return "DOCUMENT_WIDE"
                else:
                    return "TOPIC_WIDE"
                    
            return "LOCAL_SPECIFIC"

        intent = classify_query_intent(query)

        if not isinstance(top_k, int) or top_k <= 0:
            raise ValueError(
                "top_k must be a positive integer."
            )

        # Filter the corpus if a specific document is requested
        if filename:
            corpus_indices = [i for i, c in enumerate(self.chunks) if c.get("filename") == filename]
            corpus_chunks = [self.chunks[i] for i in corpus_indices]
        else:
            corpus_indices = list(range(len(self.chunks)))
            corpus_chunks = self.chunks

        actual_top_k = min(top_k, len(corpus_chunks))
        if actual_top_k == 0:
            return []

        try:
            query_embedding = embed_text(
                self.model,
                query
            )

            # --------------------------------------------------------
            # GENERIC MULTI-STRATEGY RETRIEVAL
            # --------------------------------------------------------
            
            deep_k = min(actual_top_k * 4, len(corpus_chunks))
            
            # Semantic search scoped
            semantic_results_raw = search_index(
                self.index,
                self.chunks,
                query_embedding,
                top_k=self.total_chunks if filename else min(deep_k * 2, self.total_chunks)
            )
            semantic_results = [r for r in semantic_results_raw if filename is None or r.get("filename") == filename][:deep_k]
            semantic_score_map = {res["chunk_id"]: res["score"] for res in semantic_results}

            import string
            
            def tokenize(text):
                text = re.sub(r'[^\w\s]', '', text).lower()
                return text.split()
            
            if not hasattr(self, 'bm25') or self.bm25 is None:
                from app.config import BM25_V2_INDEX_PATH
                if os.path.exists(BM25_V2_INDEX_PATH):
                    with open(BM25_V2_INDEX_PATH, "rb") as f:
                        self.bm25 = pickle.load(f)
                else:
                    from rank_bm25 import BM25Okapi
                    tokenized_corpus = [tokenize(c.get("text", "")) for c in self.chunks]
                    self.bm25 = BM25Okapi(tokenized_corpus) if tokenized_corpus else None
                    
            tokenized_query = tokenize(query)
            all_bm25_scores = self.bm25.get_scores(tokenized_query) if self.bm25 else [0.0] * self.total_chunks
            
            # Filter bm25 scores to requested document
            bm25_candidates = [(idx, all_bm25_scores[idx]) for idx in corpus_indices if all_bm25_scores[idx] > 0]
            bm25_candidates.sort(key=lambda x: x[1], reverse=True)
            bm25_top_indices = [idx for idx, _ in bm25_candidates[:deep_k]]
            
            # Candidate Fusion (RRF)
            k_rrf = 60
            fused_scores = {}
            
            for res in semantic_results:
                fused_scores[res["chunk_id"]] = 0.0
            for idx in bm25_top_indices:
                fused_scores[self.chunks[idx]["chunk_id"]] = 0.0
                
            for rank, res in enumerate(semantic_results):
                cid = res["chunk_id"]
                fused_scores[cid] += (1.0 / (k_rrf + rank + 1))
                
            for rank, idx in enumerate(bm25_top_indices):
                cid = self.chunks[idx]["chunk_id"]
                fused_scores[cid] += (1.0 / (k_rrf + rank + 1))
                
            # Modest Structural Signal
            # Boost structural chunks enough to be visible on vague queries (where they are the only matches)
            # but not enough to dominate specific queries (which score highly on both FAISS and BM25 natively).
            for cid in corpus_indices:
                chunk = self.chunks[cid]
                if chunk.get("is_structural", False):
                    if all_bm25_scores[cid] > 0 or cid in semantic_score_map:
                        if cid not in fused_scores:
                            fused_scores[cid] = 0.0
                        fused_scores[cid] += 0.02

            # Reranking / Selection
            ranked_cids = sorted(
                fused_scores.keys(),
                key=lambda cid: fused_scores[cid],
                reverse=True
            )[:actual_top_k]
            
            # Context Assembly (expand neighbors and merge into seed chunks)
            assembled_results = []
            seen_cids = set()
            
            def tokenize_set(text):
                text = re.sub(r'[^\w\s]', '', text).lower()
                return set(text.split())

            query_tokens = tokenize_set(query)

            # Normalized query tokens used ONLY for structural heading overlap matching.
            # Generic framing/stop words are stripped so that query phrasing such as
            # "compare different types of X" does not accidentally score higher against
            # a heading containing "types" than against the actual subject heading "X".
            _HEADING_MATCH_STRIP_WORDS = {
                "compare", "different", "types", "type", "kinds", "kind",
                "categories", "category", "of", "in", "this", "document",
                "mentioned", "are", "what", "tell", "explain", "how",
            }
            heading_match_tokens = query_tokens - _HEADING_MATCH_STRIP_WORDS

            # Structural Resolution: if a structural chunk matches, find its best heading and boost chunks with that heading
            structural_target_headings = {}
            for cid in ranked_cids[:deep_k]:
                chunk = self.chunks[cid]
                if chunk.get("is_structural"):
                    lines = chunk.get("text", "").split('\n')
                    headings_in_chunk = [line.strip('- ').strip() for line in lines if line.strip().startswith('-')]
                    best_heading = None
                    best_score = 0
                    for h in headings_in_chunk:
                        h_tokens = tokenize_set(h)
                        overlap = len(h_tokens.intersection(heading_match_tokens))
                        if overlap > best_score:
                            best_score = overlap
                            best_heading = h
                    if best_heading and best_score > 0:
                        current = structural_target_headings.get(best_heading, 0.0)
                        # Inherit the structural metadata's fused score as evidence for the section
                        structural_target_headings[best_heading] = max(current, fused_scores[cid])
                        
            if structural_target_headings:
                for cid in corpus_indices:
                    heading = self.chunks[cid].get("heading")
                    if heading in structural_target_headings:
                        if cid not in fused_scores:
                            fused_scores[cid] = 0.0
                        # Add the inherited structural score to the chunk's native semantic/lexical score
                        fused_scores[cid] += (structural_target_headings[heading] + 0.001)

            # Re-sort after structural resolution boost
            ranked_cids = sorted(
                fused_scores.keys(),
                key=lambda cid: fused_scores[cid],
                reverse=True
            )

            max_total_chunks = 8
            assembled_results = []
            seen_cids = set()
            
            if intent == "DOCUMENT_WIDE":
                # 1. Structural Chunks (up to 2)
                struct_cids = [cid for cid in corpus_indices if self.chunks[cid].get("is_structural")]
                struct_cids.sort(key=lambda x: self.chunks[x]["chunk_id"])
                
                added_struct = 0
                for cid in struct_cids:
                    if added_struct >= 2:
                        break
                    if cid not in seen_cids:
                        chunk = self.chunks[cid].copy()
                        seen_cids.add(cid)
                        assembled_results.append(chunk)
                        added_struct += 1
                
                # 2. Introductory Chunks (up to 2)
                intro_cids = [cid for cid in corpus_indices if not self.chunks[cid].get("is_structural")]
                intro_cids.sort(key=lambda x: self.chunks[x]["chunk_id"])
                
                added_intro = 0
                for cid in intro_cids:
                    if added_intro >= 2:
                        break
                    if cid not in seen_cids:
                        chunk = self.chunks[cid].copy()
                        seen_cids.add(cid)
                        assembled_results.append(chunk)
                        added_intro += 1

            seen_headings = set()
            second_pass_cids = []
            
            ranked_cids = ranked_cids[:actual_top_k * 2]
            
            for cid in ranked_cids:
                if cid in seen_cids:
                    continue
                chunk = self.chunks[cid]
                heading = chunk.get("heading") or chunk.get("filename") or "Unknown"
                
                if heading not in seen_headings:
                    seen_headings.add(heading)
                    if len(assembled_results) < max_total_chunks:
                        seen_cids.add(cid)
                        assembled_results.append(chunk.copy())
                    else:
                        break
                else:
                    second_pass_cids.append(cid)
                    
            for cid in second_pass_cids:
                if len(assembled_results) < max_total_chunks:
                    if cid not in seen_cids:
                        seen_cids.add(cid)
                        assembled_results.append(self.chunks[cid].copy())
                else:
                    break

            final_results = []
            for chunk in assembled_results:
                if filename and chunk.get("filename") != filename:
                    raise RuntimeError(f"Internal retrieval error: retrieved chunk {chunk['chunk_id']} from {chunk.get('filename')} but requested {filename}")
                
                cid = chunk["chunk_id"]
                chunk["fused_score"] = fused_scores.get(cid, 0.0)
                chunk["score"] = semantic_score_map.get(cid, 0.0)
                if hasattr(self, 'bm25') and self.bm25:
                    chunk["lexical_score"] = all_bm25_scores[cid]
                else:
                    chunk["lexical_score"] = 0.0
                final_results.append(chunk)

            # Preserve document order
            final_results.sort(key=lambda x: x["chunk_id"])
            for rank, chunk in enumerate(final_results):
                chunk["rank"] = rank + 1

            return final_results

        except Exception as e:
            raise RuntimeError(
                f"Embedding or FAISS search failed: {e}"
            )


# ========================================================================
# CLI DEBUG MODE
# ========================================================================

if __name__ == "__main__":

    try:
        print("Initializing Retriever (Cold Start)...")

        retriever = Retriever()

        print(
            f"Index loaded. Total chunks: "
            f"{retriever.total_chunks}"
        )

        while True:

            query = input(
                "\nEnter query (or 'exit' to quit): "
            ).strip()

            if query.lower() in ["exit", "quit"]:
                break

            if not query:
                continue

            start = time.perf_counter()

            try:
                results = retriever.retrieve(
                    query,
                    top_k=3
                )

                latency = time.perf_counter() - start

                print(
                    f"Found {len(results)} results "
                    f"in {latency:.4f}s"
                )

                for result in results:

                    print(
                        f"[{result['rank']}] "
                        f"Score: {result['score']:.4f} | "
                        f"File: {result['filename']} | "
                        f"Page: {result.get('page')}"
                    )

                    print(
                        f"    Excerpt: "
                        f"{result['text'][:500]}..."
                    )

            except Exception as e:
                print(f"Error: {e}")

    except Exception as e:
        print(f"Initialization Error: {e}")
