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
            "7. EVERY factual claim in your answer MUST have supporting source citations using the provided Source IDs (e.g., [S1], [S2]).\n"
            "8. Put the citation immediately after the claim or sentence it supports.\n"
            "9. Multiple sources may be cited together when appropriate (e.g., [S1][S2]).\n"
            "10. Use ONLY the supplied source IDs. Do not invent source IDs, and do not cite sources that do not support the claim.\n\n"
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
        filename: str = None
    ) -> Dict[str, Any]:

        chunks = self.retriever.retrieve(
            query=query,
            top_k=top_k,
            filename=filename
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
                    chunk.get("text", "") + "\n" + str(chunk.get("heading", ""))
                )
                for chunk in chunks
            )

        # Normal questions still require the grounding threshold.
        #
        # Explicit Program queries bypass it ONLY when the exact
        # requested Program heading was retrieved.
        max_semantic = max((chunk.get("score", 0.0) for chunk in chunks), default=0.0)
        max_lexical = max((chunk.get("lexical_score", 0.0) for chunk in chunks), default=0.0)
        has_structural = any(chunk.get("is_structural", False) for chunk in chunks)
        
        is_grounded = False
        if max_semantic >= INITIAL_GROUNDING_THRESHOLD:
            is_grounded = True
        elif has_structural and max_lexical > 0:
            # If structural metadata was retrieved because of a lexical match
            is_grounded = True
            
        if not is_grounded and not has_exact_program:
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
        first_raw_output = self.llm.generate(prompt, max_tokens=768)
        raw_output = first_raw_output

        # Convert [S1], [S2], etc. into actual document citations.
        final_answer, used_chunks = self.parse_citations(
            raw_output,
            chunks,
        )

        is_refusal = "The provided documents do not contain" in raw_output
        retry_triggered = False

        if not is_refusal and len(used_chunks) == 0:
            retry_triggered = True
            retry_prompt = prompt + "\n\nCRITICAL: Your previous response did not include valid source citations. Rewrite the answer using ONLY the provided context. Every factual claim must include the appropriate [S#] source citation immediately after the claim. Use only the provided source IDs. Do not invent source IDs."
            
            raw_output = self.llm.generate(retry_prompt, max_tokens=768)
            final_answer, used_chunks = self.parse_citations(
                raw_output,
                chunks,
            )
            
            if len(used_chunks) == 0:
                return {
                    "answer": "The generated answer could not be returned because it lacked sufficient source citations.",
                    "used_chunks": [],
                    "retrieved_chunks": chunks,
                    "raw_llm_output": raw_output,
                    "retry_triggered": retry_triggered,
                    "first_raw_output": first_raw_output,
                }

        return {
            "answer": final_answer,
            "used_chunks": used_chunks,
            "retrieved_chunks": chunks,
            "raw_llm_output": raw_output,
            "retry_triggered": retry_triggered,
            "first_raw_output": first_raw_output,
        }