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


def save_index(index, chunks, index_path=INDEX_PATH, metadata_path=METADATA_PATH):
    """
    Save the FAISS index and chunk metadata to disk.
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


def load_index(index_path=INDEX_PATH, metadata_path=METADATA_PATH):
    """
    Load a previously saved FAISS index and its metadata.
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

    return index, chunks


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