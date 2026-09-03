import re
with open("/home/nova/Desktop/RAG/app/retrieve.py", "r") as f:
    content = f.read()

orig_loop = """                # Check global limits BEFORE doing the backwards/forwards check, 
                # but ONLY break if we already exceeded it. Otherwise, we might add 0 results if top_k is big.
                if total_chunks >= max_total_chunks and len(assembled_results) >= max_total_chunks:
                    break"""

new_loop = """                if total_chunks >= max_total_chunks:
                    break"""
content = content.replace(orig_loop, new_loop)

orig_inner = """                    if total_chunks >= max_total_chunks and len(assembled_results) >= max_total_chunks:
                        break"""

new_inner = """                    if total_chunks >= max_total_chunks:
                        break"""
content = content.replace(orig_inner, new_inner)

# Set expansion_limit back to 8
content = content.replace("expansion_limit = 1", "expansion_limit = 8")

with open("/home/nova/Desktop/RAG/app/retrieve.py", "w") as f:
    f.write(content)
