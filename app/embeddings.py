import time

from sentence_transformers import SentenceTransformer


from app.config import EMBEDDING_MODEL_NAME

MODEL_NAME = EMBEDDING_MODEL_NAME


def load_embedding_model():
    """
    Load the local embedding model.
    """

    model = SentenceTransformer(MODEL_NAME)

    return model


def embed_text(model, text):
    """
    Convert a single piece of text into an embedding vector.
    """

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding


def embed_chunks(model, chunks):
    """
    Convert multiple chunks into embedding vectors.

    Returns:
        embeddings: list of vectors
    """

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    return embeddings


if __name__ == "__main__":

    print(f"Loading embedding model: {MODEL_NAME}")

    start_time = time.perf_counter()

    model = load_embedding_model()

    model_load_time = time.perf_counter() - start_time

    print(
        f"\nModel loading time: "
        f"{model_load_time:.2f} seconds"
    )

    test_text = (
        "Naive Bayes classification works "
        "using Bayes theorem."
    )

    embedding = embed_text(
        model,
        test_text
    )

    print("\n===== SINGLE EMBEDDING TEST =====")

    print(f"Input text: {test_text}")
    print(f"Vector dimensions: {len(embedding)}")

    print("\nFirst 10 values:")

    for value in embedding[:10]:
        print(f"{value:.6f}")