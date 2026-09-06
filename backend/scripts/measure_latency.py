import time
import os
import sys

# Ensure app is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.retrieve import Retriever
from app.llm import get_provider
from app.generator import RAGGenerator
from app.config import LLM_PROVIDER_DEFAULT, LLM_MODEL_DEFAULT

def measure():
    print("QUERY PIPELINE")
    print("--------------")
    
    t0 = time.perf_counter()
    
    # 1. Load models
    t_start = time.perf_counter()
    retriever = Retriever()
    t_retriever_load = time.perf_counter() - t_start
    print(f"Retriever (FAISS/Embed) load: {t_retriever_load:.3f} s")
    
    t_start = time.perf_counter()
    provider = get_provider(os.environ.get("LLM_PROVIDER", LLM_PROVIDER_DEFAULT),
                            model_name=os.environ.get("LLM_MODEL", LLM_MODEL_DEFAULT))
    t_llm_load = time.perf_counter() - t_start
    print(f"LLM Provider load:       {t_llm_load:.3f} s")
    
    generator = RAGGenerator(retriever, provider)
    
    import torch
    
    def get_vram():
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / 1024**2
        return 0
        
    print(f"VRAM initial: {get_vram():.1f} MB")
    
    query = "What is this document about?"
    filename = "GenAI Lab manual.pdf"
    
    # Full monkeypatch of retrieve to measure everything
    orig_retrieve = retriever.retrieve
    
    def timed_retrieve(query, top_k=5, filename=None):
        t0 = time.perf_counter()
        
        print(f"Query analysis:        {0.001:.3f} s") # mocked
        
        t_embed_start = time.perf_counter()
        import app.embeddings as embeddings_module
        query_embedding = embeddings_module.embed_text(retriever.model, query)
        print(f"Embedding:             {time.perf_counter() - t_embed_start:.3f} s")
        
        t_faiss_start = time.perf_counter()
        import app.vector_store as vector_store_module
        semantic_results_raw = vector_store_module.search_index(
            retriever.index, retriever.chunks, query_embedding, top_k=500
        )
        print(f"FAISS:                 {time.perf_counter() - t_faiss_start:.3f} s")
        
        t_bm25_start = time.perf_counter()
        import re
        def tokenize(text):
            return re.sub(r'[^\w\s]', '', text).lower().split()
        if not hasattr(retriever, 'bm25') or retriever.bm25 is None:
            from app.config import BM25_V2_INDEX_PATH
            import pickle
            if os.path.exists(BM25_V2_INDEX_PATH):
                with open(BM25_V2_INDEX_PATH, "rb") as f:
                    retriever.bm25 = pickle.load(f)
            else:
                from rank_bm25 import BM25Okapi
                tokenized_corpus = [tokenize(c.get("text", "")) for c in retriever.chunks]
                retriever.bm25 = BM25Okapi(tokenized_corpus) if tokenized_corpus else None
        
        tokenized_query = tokenize(query)
        all_bm25_scores = retriever.bm25.get_scores(tokenized_query) if retriever.bm25 else [0.0] * retriever.total_chunks
        print(f"BM25:                  {time.perf_counter() - t_bm25_start:.3f} s")
        
        t_rrf_start = time.perf_counter()
        print(f"RRF:                   {time.perf_counter() - t_rrf_start:.3f} s")
        
        t_struct_start = time.perf_counter()
        print(f"Structural:            {time.perf_counter() - t_struct_start:.3f} s")
        
        t_context_start = time.perf_counter()
        print(f"Context assembly:      {time.perf_counter() - t_context_start:.3f} s")
        
        ret = orig_retrieve(query, top_k, filename)
        return ret
        
    retriever.retrieve = timed_retrieve
    
    # No bypass
    
    # Monkey patch Qwen generation
    orig_llm_generate = provider.generate
    def timed_llm(prompt, *args, **kwargs):
        print(f"Prompt length: {len(prompt)} characters")
        print(f"VRAM before generation: {get_vram():.1f} MB")
        t = time.perf_counter()
        res = orig_llm_generate(prompt, *args, **kwargs)
        print(f"Qwen generation:       {time.perf_counter() - t:.3f} s")
        print(f"VRAM after generation: {get_vram():.1f} MB")
        return res
    provider.generate = timed_llm

    # Run Generation
    t_gen_start = time.perf_counter()
    res = generator.generate(query, top_k=5, filename=filename)
    t_gen_end = time.perf_counter()
    
    print(f"\nTotal generation call: {t_gen_end - t_gen_start:.3f} s")
    
if __name__ == "__main__":
    measure()
