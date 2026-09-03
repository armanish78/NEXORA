import json
import time
import os
import hashlib
import pickle
from pathlib import Path
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL_NAME,
    EMBEDDINGS_DIR,
    FAISS_V2_INDEX_PATH,
    CHUNKS_V2_METADATA_PATH
)
from app.chunking import chunk_pages
from app.embeddings import load_embedding_model, embed_chunks
from app.vector_store import create_index, save_index
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def compute_document_state_hash(pages_json_str, chunk_size, chunk_overlap, model_name):
    hasher = hashlib.sha256()
    hasher.update(pages_json_str.encode("utf-8"))
    hasher.update(str(chunk_size).encode("utf-8"))
    hasher.update(str(chunk_overlap).encode("utf-8"))
    hasher.update(model_name.encode("utf-8"))
    return hasher.hexdigest()

def verify_cache_integrity(cached_data, expected_hash, chunk_size, chunk_overlap, model_name):
    if cached_data.get("hash") != expected_hash:
        return False
    if cached_data.get("chunk_size") != chunk_size:
        return False
    if cached_data.get("chunk_overlap") != chunk_overlap:
        return False
    if cached_data.get("model_name") != model_name:
        return False
        
    chunks = cached_data.get("chunks", [])
    if not chunks:
        return False
        
    # Check dimensions and types
    for i, c in enumerate(chunks):
        if c["chunk_id"] != i:
            return False
        if "embedding" not in c:
            return False
        if len(c["embedding"]) == 0:
            return False
            
    return True

def main():
    cleaned_dir = Path("data/cleaned")
    if not cleaned_dir.exists():
        logger.error(f"Directory not found: {cleaned_dir}")
        return
        
    model = None
    
    total_docs = 0
    cache_hits = 0
    cache_misses = 0
    
    global_chunks = []
    
    # Timers
    t_hash = 0.0
    t_chunk = 0.0
    t_model_load = 0.0
    t_embed = 0.0
    
    t_start_total = time.perf_counter()
    
    for json_file in sorted(cleaned_dir.glob("*.json")):
        total_docs += 1
        logger.info(f"Processing: {json_file.name}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            pages_json_str = f.read()
            pages = json.loads(pages_json_str)
            
        t0 = time.perf_counter()
        doc_hash = compute_document_state_hash(pages_json_str, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL_NAME)
        t_hash += (time.perf_counter() - t0)
        
        cache_path = os.path.join(EMBEDDINGS_DIR, f"{json_file.stem}.pkl")
        
        cache_valid = False
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "rb") as f:
                    cached_data = pickle.load(f)
                if verify_cache_integrity(cached_data, doc_hash, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL_NAME):
                    cache_valid = True
                    cache_hits += 1
                    logger.info(f"  Cache HIT: {json_file.name}")
                    
                    for c in cached_data["chunks"]:
                        global_chunks.append(c)
            except Exception as e:
                logger.warning(f"  Cache read error for {json_file.name}: {e}")
                
        if not cache_valid:
            cache_misses += 1
            logger.info(f"  Cache MISS: {json_file.name}")
            
            t0 = time.perf_counter()
            chunks = chunk_pages(pages, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
            # Assign source_hash for provenance
            for i, c in enumerate(chunks):
                c["source_hash"] = doc_hash
                c["chunk_id"] = i
            t_chunk += (time.perf_counter() - t0)
            
            if not chunks:
                continue
                
            if model is None:
                t0 = time.perf_counter()
                model = load_embedding_model()
                t_model_load += (time.perf_counter() - t0)
                
            t0 = time.perf_counter()
            embeddings = embed_chunks(model, chunks)
            t_embed += (time.perf_counter() - t0)
            
            # Attach embeddings
            for c, emb in zip(chunks, embeddings):
                c["embedding"] = emb.tolist()
                
            # Save cache
            cache_data = {
                "hash": doc_hash,
                "chunk_size": CHUNK_SIZE,
                "chunk_overlap": CHUNK_OVERLAP,
                "model_name": EMBEDDING_MODEL_NAME,
                "chunks": chunks
            }
            with open(cache_path, "wb") as f:
                pickle.dump(cache_data, f)
                
            for c in chunks:
                global_chunks.append(c)
                
    if not global_chunks:
        logger.error("No chunks to index.")
        return
        
    # Make chunk_id globally unique across all documents
    for i, c in enumerate(global_chunks):
        c["chunk_id"] = i
        
    logger.info(f"Building index with {len(global_chunks)} total chunks...")
    
    from rank_bm25 import BM25Okapi
    import re
    
    t0 = time.perf_counter()
    # Extract embeddings and clean chunks
    embeddings_matrix = [c.pop("embedding") for c in global_chunks]
    index = create_index(embeddings_matrix)
    
    # Tokenize corpus and build BM25
    tokenized_corpus = [re.sub(r'[^\w\s]', '', c.get("text", "")).lower().split() for c in global_chunks]
    bm25_model = BM25Okapi(tokenized_corpus) if tokenized_corpus else None
    t_index_build = time.perf_counter() - t0
    
    from app.config import BM25_V2_INDEX_PATH
    t0 = time.perf_counter()
    save_index(index, global_chunks, bm25_model=bm25_model, index_path=FAISS_V2_INDEX_PATH, metadata_path=CHUNKS_V2_METADATA_PATH, bm25_path=BM25_V2_INDEX_PATH)
    t_index_save = time.perf_counter() - t0
    
    t_total = time.perf_counter() - t_start_total
    
    print("\n" + "="*50)
    print("INDEXING PERFORMANCE REPORT")
    print("="*50)
    print(f"Total documents: {total_docs}")
    print(f"Cache hits:      {cache_hits}")
    print(f"Cache misses:    {cache_misses}")
    print(f"Total chunks:    {len(global_chunks)}")
    print("-"*50)
    print(f"Hashing time:        {t_hash:.4f}s")
    print(f"Chunking time:       {t_chunk:.4f}s")
    print(f"Model load time:     {t_model_load:.4f}s")
    print(f"Embedding time:      {t_embed:.4f}s")
    print(f"Index build time:    {t_index_build:.4f}s")
    print(f"Index save time:     {t_index_save:.4f}s")
    print(f"Total time:          {t_total:.4f}s")
    print("="*50)

if __name__ == "__main__":
    main()
