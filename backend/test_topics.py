from app.vector_store import load_index

_, chunks, _ = load_index()
print(f"Total chunks: {len(chunks)}")
found_topics = set()
for c in chunks:
    fn = c.get("filename")
    h = c.get("heading")
    print(f"Chunk filename: {fn}, heading: {h}")
    if fn == "BIS613D-module-3-pdf.pdf":
        if h and h != "Document Outline":
            found_topics.add(h)
print(f"\nTopics found: {list(found_topics)}")
