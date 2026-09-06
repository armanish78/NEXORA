import os

# ============================================================
# DIRECTORY CONFIGURATION
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
CLEANED_DATA_DIR = os.path.join(DATA_DIR, "cleaned")

MODEL_DIR = os.path.join(BASE_DIR, "model")
EMBEDDINGS_DIR = os.path.join(MODEL_DIR, "embeddings")
INDEXES_DIR = os.path.join(MODEL_DIR, "indexes")
CACHE_DIR = os.path.join(MODEL_DIR, "cache")

# Create directories if they do not exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, CLEANED_DATA_DIR, EMBEDDINGS_DIR, INDEXES_DIR, CACHE_DIR]:
    os.makedirs(directory, exist_ok=True)

# ============================================================
# DATABASE CONFIGURATION
# ============================================================
DB_PATH = os.path.join(DATA_DIR, "study_assistant.db")

# ============================================================
# LLM CONFIGURATION
# ============================================================
LLM_PROVIDER_DEFAULT = "huggingface"
LLM_MODEL_DEFAULT = "Qwen/Qwen2.5-3B-Instruct"

# ============================================================
# INGESTION & CHUNKING CONFIGURATION
# ============================================================
CHUNK_SIZE = 512
CHUNK_OVERLAP = 0
MINIMUM_CHUNK_SIZE = 0

# ============================================================
# EMBEDDING CONFIGURATION
# ============================================================
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# ============================================================
# RETRIEVAL CONFIGURATION
# ============================================================
TOP_K_RETRIEVAL = 5

# An empirically selected initial threshold for the current all-MiniLM-L6-v2 embedding model and current corpus.
# It must be recalibrated if the embedding model, corpus characteristics, chunking strategy, or retrieval metric changes.
INITIAL_GROUNDING_THRESHOLD = 0.35

# ============================================================
# INDEX PATHS
# ============================================================
V1_INDEX_DIR = os.path.join(INDEXES_DIR, "v1")
V2_INDEX_DIR = os.path.join(INDEXES_DIR, "v2")

os.makedirs(V1_INDEX_DIR, exist_ok=True)
os.makedirs(V2_INDEX_DIR, exist_ok=True)

# Deprecated/V1 backwards compatibility
FAISS_INDEX_PATH = os.path.join(V1_INDEX_DIR, "faiss.index")
CHUNKS_METADATA_PATH = os.path.join(V1_INDEX_DIR, "chunks.pkl")

# V2 Index Paths
FAISS_V2_INDEX_PATH = os.path.join(V2_INDEX_DIR, "faiss.index")
CHUNKS_V2_METADATA_PATH = os.path.join(V2_INDEX_DIR, "chunks.pkl")
BM25_V2_INDEX_PATH = os.path.join(V2_INDEX_DIR, "bm25.pkl")
