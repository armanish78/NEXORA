from app.vector_store import load_index

_, chunks, _ = load_index()
topics = set()
for chunk in chunks:
    heading = chunk.get("heading")
    if heading and heading != "Document Outline":
        topics.add(heading)
print(f"\nTopics found ({len(topics)}): {list(topics)[:5]}")
