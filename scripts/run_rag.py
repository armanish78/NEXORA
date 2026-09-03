import sys
import os
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv is optional if env vars are set externally

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.retrieve import Retriever
from app.llm import get_provider
from app.generator import RAGGenerator
from app.config import INDEXES_DIR, LLM_PROVIDER_DEFAULT, LLM_MODEL_DEFAULT

def run_interactive():
    print("\nLoading Educational RAG Assistant...")
    t0 = time.perf_counter()
    
    # 1. Initialize Retriever
    try:
        print("Loading Retriever (FAISS V2)... ", end="", flush=True)
        v2_index = os.path.join(INDEXES_DIR, "v2", "faiss.index")
        v2_meta = os.path.join(INDEXES_DIR, "v2", "chunks.pkl")
        if not os.path.exists(v2_index) or not os.path.exists(v2_meta):
            print("\nError: FAISS index not found. Please run scripts/run_indexing.py first.")
            sys.exit(1)
            
        faiss = Retriever(index_path=v2_index, metadata_path=v2_meta)
        print("Done.")
    except Exception as e:
        print(f"\nFailed to load Retriever: {str(e)}")
        sys.exit(1)
        
    # 2. Initialize LLM
    try:
        provider_name = os.environ.get("LLM_PROVIDER", LLM_PROVIDER_DEFAULT)
        model_name = os.environ.get("LLM_MODEL", LLM_MODEL_DEFAULT)
        print(f"Loading LLM ({model_name} via {provider_name})... ", end="", flush=True)
        
        provider = get_provider(provider_name, model_name=model_name)
        generator = RAGGenerator(faiss, provider)
        print("Done.")
    except Exception as e:
        print(f"\nFailed to load LLM: {str(e)}")
        if "CUDA out of memory" in str(e):
            print("CUDA Out Of Memory: Try closing other GPU applications or selecting a smaller model.")
        sys.exit(1)
        
    t1 = time.perf_counter()
    print(f"Ready. (Startup took {t1-t0:.2f}s)")
    filenames = sorted(list(set(c.get("filename") for c in faiss.chunks if c.get("filename"))))
    print("\nAvailable indexed documents:")
    print("0. All documents (No filter)")
    for i, fname in enumerate(filenames, 1):
        print(f"{i}. {fname}")
        
    selected_file = None
    while True:
        choice = input("\nSelect active document by number (default 0): ").strip()
        if not choice:
            break
        try:
            idx = int(choice)
            if idx == 0:
                break
            elif 1 <= idx <= len(filenames):
                selected_file = filenames[idx - 1]
                break
        except ValueError:
            pass
        print("Invalid choice. Try again.")
        
    print(f"\nActive Document Scope: {selected_file if selected_file else 'ALL DOCUMENTS'}")

    print("\n" + "="*50)
    print("Ask a question! (Type 'quit', 'exit', or Ctrl+C to exit)")
    print("="*50)
    
    while True:
        try:
            q = input("\nQuestion: ").strip()
            if q.lower() in ['quit', 'exit', 'q']:
                print("Exiting...")
                break
            if not q:
                continue
                
            t_start = time.perf_counter()
            res = generator.generate(q, top_k=5, filename=selected_file)
            t_end = time.perf_counter()
            
            print(f"\nAnswer:\n{res['answer']}")
            
            if res["used_chunks"]:
                print("\nSources:")
                for c in res["used_chunks"]:
                    print(f"- {c['filename']}, Page {c['page']}")
                    
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred during generation: {str(e)}")
            
if __name__ == "__main__":
    run_interactive()
