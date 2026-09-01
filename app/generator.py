import re
from typing import List, Dict, Any, Tuple
from app.llm import LLMProvider

class RAGGenerator:
    def __init__(self, retriever, llm_provider: LLMProvider):
        self.retriever = retriever
        self.llm = llm_provider
        
    def generate_prompt(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        prompt = (
            "You are an intelligent educational assistant. Answer the user's question using ONLY the provided context.\n"
            "If the answer is not contained in the context, explicitly state: 'The provided documents do not contain sufficient information.'\n"
            "Do not use outside knowledge. Do not invent facts.\n"
            "Cite your claims using ONLY the provided Source IDs (e.g., [S1]). Never invent source IDs.\n\n"
            "=== CONTEXT ===\n"
        )
        
        for idx, chunk in enumerate(chunks, start=1):
            prompt += f"[S{idx}]\n"
            prompt += f"Content: {chunk['text']}\n\n"
            
        prompt += f"=== QUESTION ===\n{query}\n\nAnswer:"
        return prompt
        
    def parse_citations(self, text: str, chunks: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Replaces [Sx] in text with real metadata citations like [file.pdf, Page y].
        Returns the parsed text and the list of used chunks.
        """
        used_chunks = []
        
        def replacer(match):
            sid_str = match.group(1)
            try:
                sid = int(sid_str)
                if 1 <= sid <= len(chunks):
                    chunk = chunks[sid - 1]
                    if chunk not in used_chunks:
                        used_chunks.append(chunk)
                    return f"[{chunk['filename']}, Page {chunk['page']}]"
                else:
                    return match.group(0) # Invalid ID, leave as is
            except ValueError:
                return match.group(0)
                
        parsed_text = re.sub(r'\[S(\d+)\]', replacer, text)
        return parsed_text, used_chunks

    def generate(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        # 1. Retrieve
        chunks = self.retriever.retrieve(query, top_k=top_k)
        
        from app.config import INITIAL_GROUNDING_THRESHOLD

        # If no context found or context is below threshold
        if not chunks or chunks[0].get("score", 0) < INITIAL_GROUNDING_THRESHOLD:
            return {
                "answer": "The provided documents do not contain sufficient information.",
                "used_chunks": [],
                "retrieved_chunks": chunks,
                "raw_llm_output": ""
            }
            
        # 2. Format
        prompt = self.generate_prompt(query, chunks)
        
        # 3. Generate
        raw_output = self.llm.generate(prompt)
        
        # 4. Resolve citations
        final_answer, used_chunks = self.parse_citations(raw_output, chunks)
        
        return {
            "answer": final_answer,
            "used_chunks": used_chunks,
            "retrieved_chunks": chunks,
            "raw_llm_output": raw_output
        }
