import time
import os
from typing import List, Dict, Any

from app.embeddings import load_embedding_model, embed_text
from app.vector_store import load_index, search_index
from app.config import FAISS_V2_INDEX_PATH, CHUNKS_V2_METADATA_PATH

class Retriever:
    """
    Stateful retrieval component that manages memory efficiently
    by loading the embedding model and FAISS index exactly once.
    """
    
    def __init__(self, index_path: str = FAISS_V2_INDEX_PATH, metadata_path: str = CHUNKS_V2_METADATA_PATH):
        self.index_path = index_path
        self.metadata_path = metadata_path
        
        if not os.path.exists(self.index_path) or not os.path.exists(self.metadata_path):
            raise FileNotFoundError("FAISS index or metadata not found. Please run the indexing pipeline first.")
            
        # Cold start loads
        self.model = load_embedding_model()
        self.index, self.chunks = load_index(self.index_path, self.metadata_path)
        self.total_chunks = len(self.chunks)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Execute a semantic search query against the FAISS index.
        
        Args:
            query (str): The search query.
            top_k (int): The number of relevant chunks to return.
            
        Returns:
            List[Dict]: A list of chunks matching the query, sorted by relevance score.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty or whitespace.")
            
        if not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer.")
            
        # Limit top_k to the size of the index to prevent FAISS errors
        actual_top_k = min(top_k, self.total_chunks)
        
        if actual_top_k == 0:
            return []

        try:
            query_embedding = embed_text(self.model, query)
            
            # search_index handles the actual lookup in the FAISS structure
            results = search_index(
                self.index,
                self.chunks,
                query_embedding,
                top_k=actual_top_k
            )
            
            # The search_index function copies the chunks and appends a "score".
            # We add a "rank" for clearer provenance downstream.
            for i, res in enumerate(results):
                res["rank"] = i + 1
                
                # Adjacent Chunk Expansion
                # To solve CHUNK_OVERLAP=0 issues, we expand the text to include the adjacent chunks.
                cid = res["chunk_id"]
                filename = res.get("filename")
                expanded_text = res["text"]
                
                # Prepend previous chunk if it belongs to the same file
                if cid - 1 >= 0:
                    prev_chunk = self.chunks[cid - 1]
                    if prev_chunk.get("filename") == filename:
                        expanded_text = prev_chunk["text"] + "\n\n---\n\n" + expanded_text
                        
                # Append next chunk if it belongs to the same file
                if cid + 1 < self.total_chunks:
                    next_chunk = self.chunks[cid + 1]
                    if next_chunk.get("filename") == filename:
                        expanded_text = expanded_text + "\n\n---\n\n" + next_chunk["text"]
                        
                res["text"] = expanded_text
                
            return results
        except Exception as e:
            raise RuntimeError(f"Embedding or FAISS search failed: {e}")

if __name__ == "__main__":
    # Simple CLI loop for manual debugging
    try:
        print("Initializing Retriever (Cold Start)...")
        retriever = Retriever()
        print(f"Index loaded. Total chunks: {retriever.total_chunks}")
        
        while True:
            query = input("\nEnter query (or 'exit' to quit): ").strip()
            if query.lower() in ['exit', 'quit']:
                break
            if not query:
                continue
                
            start = time.perf_counter()
            try:
                results = retriever.retrieve(query, top_k=3)
                latency = time.perf_counter() - start
                
                print(f"Found {len(results)} results in {latency:.4f}s")
                for r in results:
                    print(f"[{r['rank']}] Score: {r['score']:.4f} | File: {r['filename']} | Page: {r.get('page')}")
                    print(f"    Excerpt: {r['text'][:100]}...")
            except Exception as e:
                print(f"Error: {e}")
    except Exception as e:
        print(f"Initialization Error: {e}")
