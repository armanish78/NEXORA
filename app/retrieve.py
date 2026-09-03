import time
import re
import os
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

        self.index, self.chunks = load_index(
            self.index_path,
            self.metadata_path
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

        max_program_chunks = max(top_k, 6)

        for cid in range(
            start_id,
            min(
                next_program_id,
                start_id + max_program_chunks
            )
        ):
            chunk = self.chunks[cid]

            # Only use chunks from the same file.
            if (
                heading_result is not None
                and chunk.get("filename")
                != heading_result.get("filename")
            ):
                break

            program_chunks.append(
                {
                    **chunk,
                    "score": (
                        heading_result.get("score", 0.0)
                        if cid == start_id
                        else 0.0
                    )
                }
            )

        # ------------------------------------------------------------
        # Put the heading first.
        # ------------------------------------------------------------

        program_chunks.sort(
            key=lambda x: x["chunk_id"]
        )

        return program_chunks[:max_program_chunks]

    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:

        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty or whitespace."
            )

        if not isinstance(top_k, int) or top_k <= 0:
            raise ValueError(
                "top_k must be a positive integer."
            )

        actual_top_k = min(
            top_k,
            self.total_chunks
        )

        if actual_top_k == 0:
            return []

        try:
            # --------------------------------------------------------
            # Embed query
            # --------------------------------------------------------

            query_embedding = embed_text(
                self.model,
                query
            )

            # --------------------------------------------------------
            # Detect explicit Program N
            # --------------------------------------------------------

            program_match = re.search(
                r"\bprogram\s*[-]?\s*(\d+)\b",
                query,
                re.IGNORECASE
            )

            # --------------------------------------------------------
            # Program-specific retrieval
            # --------------------------------------------------------

            if program_match:

                program_number = program_match.group(1)

                # Search entire index to guarantee that the exact
                # program heading can be located.
                semantic_results = search_index(
                    self.index,
                    self.chunks,
                    query_embedding,
                    top_k=self.total_chunks
                )

                results = self._find_program_chunks(
                    program_number,
                    semantic_results,
                    actual_top_k
                )

                # If exact heading wasn't found, fall back to
                # semantic retrieval rather than returning nothing.
                if not results:
                    results = semantic_results[:actual_top_k]

            # --------------------------------------------------------
            # Normal semantic retrieval
            # --------------------------------------------------------

            else:

                results = search_index(
                    self.index,
                    self.chunks,
                    query_embedding,
                    top_k=actual_top_k
                )

            # --------------------------------------------------------
            # Add ranks
            # --------------------------------------------------------

            for i, result in enumerate(results):
                result["rank"] = i + 1

            return results

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