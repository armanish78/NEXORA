import os
import sys
import time
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.dependencies import init_core_brain, get_rag_generator
from app.config import INDEXES_DIR

print("Loading Core Brain...")
init_core_brain()
generator = get_rag_generator()

if torch.cuda.is_available():
    torch.cuda.reset_peak_memory_stats()
    torch.cuda.empty_cache()
    vram_before = torch.cuda.memory_allocated() / (1024 ** 2)
else:
    vram_before = 0

print(f"VRAM BEFORE: {vram_before:.2f} MB")

query = "What is this document about?"
print(f"Running Query: {query}")

t0 = time.perf_counter()
res = generator.generate(query, top_k=5)
t1 = time.perf_counter()

if torch.cuda.is_available():
    vram_peak = torch.cuda.max_memory_allocated() / (1024 ** 2)
else:
    vram_peak = 0

print(f"VRAM PEAK (DURING): {vram_peak:.2f} MB")
print(f"LATENCY: {t1-t0:.2f} seconds")

chunks_retrieved = len(res.get("retrieved_chunks", []))
final_chunks = sum(c.get("text", "").count("\n\n") + 1 for c in res.get("retrieved_chunks", []))
total_text_len = sum(len(c.get("text", "")) for c in res.get("retrieved_chunks", []))
approx_tokens = total_text_len // 4

print(f"RESULTS RETRIEVED: {chunks_retrieved}")
print(f"APPROX CONTEXT CHUNKS: {final_chunks}")
print(f"APPROX TOKENS: {approx_tokens}")
print(f"ANSWER:\n{res.get('answer', '')}")
