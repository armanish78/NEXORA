import pickle
from app.config import CHUNKS_V2_METADATA_PATH

with open(CHUNKS_V2_METADATA_PATH, "rb") as f:
    chunks = pickle.load(f)

filenames = set(c.get('filename') for c in chunks)
print('Indexed filenames:', filenames)

if filenames:
    first_file = list(filenames)[0]
    first_file_chunks = [c for c in chunks if c.get('filename') == first_file]
    if first_file_chunks:
        print(f"Sample text from {first_file}:", first_file_chunks[0].get("text")[:100])
