with open("/home/nova/Desktop/RAG/app/retrieve.py", "r") as f:
    content = f.read()

orig_logic = """                if not chunk.get("is_structural"):
                    # Expand backwards
                    for offset in range(1, expansion_limit + 1):"""

new_logic = """                if not chunk.get("is_structural") and total_chunks < max_total_chunks:
                    # Expand backwards
                    for offset in range(1, expansion_limit + 1):"""

content = content.replace(orig_logic, new_logic)

orig_inner = """                    if total_chunks >= max_total_chunks:
                        break"""
content = content.replace(orig_inner, "")

content = content.replace("expansion_limit = 4", "expansion_limit = 8")
content = content.replace("max_total_chunks = max(20, actual_top_k)", "max_total_chunks = 8")

with open("/home/nova/Desktop/RAG/app/retrieve.py", "w") as f:
    f.write(content)
