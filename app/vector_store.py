import os
import pickle

import faiss
import numpy as np


from app.config import FAISS_INDEX_PATH, CHUNKS_METADATA_PATH, INDEXES_DIR

INDEX_PATH = FAISS_INDEX_PATH
METADATA_PATH = CHUNKS_METADATA_PATH
MODEL_DIR = INDEXES_DIR


def create_index(embeddings):
    """
    Create a FAISS index for normalized embeddings.

    Because our embeddings are normalized,
    inner product is equivalent to cosine similarity.
    """

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    return index


def save_index(index, chunks, bm25_model=None, index_path=INDEX_PATH, metadata_path=METADATA_PATH, bm25_path=None):
    """
    Save the FAISS index, chunk metadata, and BM25 index to disk.
    """

    os.makedirs(
        os.path.dirname(index_path),
        exist_ok=True
    )

    faiss.write_index(
        index,
        index_path
    )

    with open(metadata_path, "wb") as file:
        pickle.dump(
            chunks,
            file
        )
        
    if bm25_model is not None and bm25_path is not None:
        os.makedirs(os.path.dirname(bm25_path), exist_ok=True)
        with open(bm25_path, "wb") as file:
            pickle.dump(bm25_model, file)


def load_index(index_path=INDEX_PATH, metadata_path=METADATA_PATH, bm25_path=None):
    """
    Load a previously saved FAISS index, its metadata, and optionally the BM25 index.
    """

    if not os.path.exists(index_path):
        raise FileNotFoundError(
            f"FAISS index not found: {index_path}"
        )

    if not os.path.exists(metadata_path):
        raise FileNotFoundError(
            f"Chunk metadata not found: {metadata_path}"
        )

    index = faiss.read_index(
        index_path
    )

    with open(metadata_path, "rb") as file:
        chunks = pickle.load(file)
        
    bm25_model = None
    if bm25_path and os.path.exists(bm25_path):
        with open(bm25_path, "rb") as file:
            bm25_model = pickle.load(file)

    return index, chunks, bm25_model


def search_index(
    index,
    chunks,
    query_embedding,
    top_k=5
):
    """
    Search the vector index and return
    the most relevant chunks.
    """

    query_embedding = np.asarray(
        [query_embedding],
        dtype="float32"
    )

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, index_position in zip(
        scores[0],
        indices[0]
    ):

        if index_position == -1:
            continue

        result = chunks[index_position].copy()

        result["score"] = float(score)

        results.append(result)

    return results