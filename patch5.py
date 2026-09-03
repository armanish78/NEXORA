with open("/home/nova/Desktop/RAG/app/retrieve.py", "r") as f:
    content = f.read()

orig_outer_break = """                if len(assembled_results) >= actual_top_k:
                    break
                if total_chunks >= max_total_chunks:
                    break"""

new_outer_break = """                if len(assembled_results) >= actual_top_k:
                    break"""

content = content.replace(orig_outer_break, new_outer_break)

with open("/home/nova/Desktop/RAG/app/retrieve.py", "w") as f:
    f.write(content)
