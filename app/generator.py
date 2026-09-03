import re
from typing import List, Dict, Any, Tuple

from app.llm import LLMProvider


class RAGGenerator:
    def __init__(
        self,
        retriever,
        llm: LLMProvider,
    ):
        self.retriever = retriever
        self.llm = llm

    def generate_prompt(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
    ) -> str:
        prompt = (
            "You are an educational assistant answering questions "
            "from a provided document.\n\n"
            "STRICT RULES:\n"
            "1. Use ONLY information present in the provided context.\n"
            "2. Text, code, comments, examples, and output shown in "
            "the context are all valid evidence.\n"
            "3. If the answer is not contained in the context, "
            "explicitly state: 'The provided documents do not contain "
            "sufficient information.'\n"
            "4. If the context contains the answer, answer the "
            "question directly. Do NOT refuse.\n"
            "5. Do not use outside knowledge. Do not invent facts.\n"
            "6. Do not invent examples.\n"
            "7. Cite supporting information using the provided "
            "Source IDs such as [S1] or [S2].\n\n"
            "=== CONTEXT ===\n"
        )

        for idx, chunk in enumerate(chunks, start=1):
            prompt += f"[S{idx}]\n"
            prompt += f"Content: {chunk['text']}\n\n"

        prompt += (
            "=== QUESTION ===\n"
            f"{query}\n\n"
            "=== ANSWER ===\n"
            "Answer directly using the relevant information above."
        )

        return prompt

    def parse_citations(
        self,
        output: str,
        chunks: List[Dict[str, Any]],
    ) -> Tuple[str, List[Dict[str, Any]]]:

        used_chunks = []

        def replace_citation(match):
            index = int(match.group(1)) - 1

            if 0 <= index < len(chunks):
                chunk = chunks[index]

                if chunk not in used_chunks:
                    used_chunks.append(chunk)

                filename = chunk.get("filename")
                page = chunk.get("page")

                if filename is not None and page is not None:
                    if isinstance(page, list):
                        if len(page) == 1:
                            page_text = str(page[0])
                        else:
                            page_text = ", ".join(
                                str(p) for p in page
                            )
                    else:
                        page_text = str(page)

                    return (
                        f"[{filename}, Page {page_text}]"
                    )

            # Invalid citation such as [S0] or [S99]
            # remains unchanged.
            return match.group(0)

        final_answer = re.sub(
            r"\[S(\d+)\]",
            replace_citation,
            output,
        )

        return final_answer.strip(), used_chunks

    def generate(
        self,
        query: str,
        top_k: int = 5,
    ) -> Dict[str, Any]:

        chunks = self.retriever.retrieve(
            query=query,
            top_k=top_k,
        )

        # No retrieved evidence.
        if not chunks:
            return {
                "answer": (
                    "The provided documents do not contain "
                    "sufficient information."
                ),
                "used_chunks": [],
                "retrieved_chunks": chunks,
                "raw_llm_output": "",
            }

        from app.config import INITIAL_GROUNDING_THRESHOLD

        # ---------------------------------------------------------
        # Explicit Program query handling
        #
        # Program queries are handled specially by the retriever.
        # It searches for the exact PROGRAM - N heading and then
        # retrieves the contiguous Program content.
        #
        # Therefore a low semantic similarity score should NOT
        # cause a valid Program query to be rejected.
        #
        # However, we only bypass the threshold when the exact
        # requested Program heading is actually present.
        # ---------------------------------------------------------

        program_match = re.search(
            r"\bprogram\s*[-]?\s*(\d+)\b",
            query,
            re.IGNORECASE,
        )

        has_exact_program = False

        if program_match:
            program_number = program_match.group(1)

            program_pattern = re.compile(
                rf"\bPROGRAM\s*-\s*{re.escape(program_number)}\b",
                re.IGNORECASE,
            )

            has_exact_program = any(
                program_pattern.search(
                    chunk.get("text", "")
                )
                for chunk in chunks
            )

        # Normal questions still require the grounding threshold.
        #
        # Explicit Program queries bypass it ONLY when the exact
        # requested Program heading was retrieved.
        if (
            not has_exact_program
            and chunks[0].get("score", 0)
            < INITIAL_GROUNDING_THRESHOLD
        ):
            return {
                "answer": (
                    "The provided documents do not contain "
                    "sufficient information."
                ),
                "used_chunks": [],
                "retrieved_chunks": chunks,
                "raw_llm_output": "",
            }

        # Build grounded prompt.
        prompt = self.generate_prompt(
            query=query,
            chunks=chunks,
        )

        # Generate answer.
        raw_output = self.llm.generate(prompt)

        # Convert [S1], [S2], etc. into actual document citations.
        final_answer, used_chunks = self.parse_citations(
            raw_output,
            chunks,
        )

        return {
            "answer": final_answer,
            "used_chunks": used_chunks,
            "retrieved_chunks": chunks,
            "raw_llm_output": raw_output,
        }