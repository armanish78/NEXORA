with open("/home/nova/Desktop/RAG/app/retrieve.py", "r") as f:
    content = f.read()

content = content.replace("expansion_limit = 8", "expansion_limit = 4")
content = content.replace("max_total_chunks = max(8, actual_top_k)", "max_total_chunks = max(20, actual_top_k)")

with open("/home/nova/Desktop/RAG/app/retrieve.py", "w") as f:
    f.write(content)
