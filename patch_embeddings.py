with open("app/embeddings.py", "r") as f:
    content = f.read()

content = content.replace(
    'model = SentenceTransformer(MODEL_NAME)',
    'print("\\n\\n[DEBUG] INSTANTIATING SENTENCETRANSFORMER!\\n\\n", flush=True)\n    model = SentenceTransformer(MODEL_NAME)'
)

with open("app/embeddings.py", "w") as f:
    f.write(content)
