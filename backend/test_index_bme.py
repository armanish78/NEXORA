from app.vector_store import load_index
import collections

_, chunks, _ = load_index()
counts = collections.Counter([c.get("filename") for c in chunks])
bme_count = 0
tmp_counts = {}
for name, count in counts.items():
    if name == "BME654B-module-2-pdf.pdf":
        bme_count = count
    elif name and "tmp" in name:
        tmp_counts[name] = count

print(f"BME654B-module-2-pdf.pdf chunks: {bme_count}")
print("tmp*.pdf chunks:")
for name, count in tmp_counts.items():
    print(f"  {name}: {count}")

