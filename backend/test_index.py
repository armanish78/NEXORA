from app.vector_store import load_index
import collections

_, chunks, _ = load_index()
counts = collections.Counter([c.get("filename") for c in chunks])
for name, count in counts.items():
    if "nexora_test_solar" in name or "tmp" in name or "BIS613D" in name:
        print(f"{name}: {count}")
