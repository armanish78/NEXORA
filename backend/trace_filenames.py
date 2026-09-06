import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.retrieve import Retriever

def main():
    r = Retriever()
    filenames = set(c.get("filename") for c in r.chunks)
    print(f"Unique filenames in metadata: {filenames}")

if __name__ == '__main__':
    main()
