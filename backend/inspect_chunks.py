from app.retrieve import load_index
try:
    index, chunks, bm25 = load_index()
    filenames = set(c.get("filename") for c in chunks)
    print(f"Total chunks: {len(chunks)}")
    print(f"Filenames in index: {filenames}")
except Exception as e:
    print(e)
