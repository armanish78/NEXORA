import requests
import time
import subprocess
import socket

def wait_for_port(port, timeout=30.0):
    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1.0):
                return True
        except OSError:
            time.sleep(1)
            if time.perf_counter() - start_time >= timeout:
                return False

server_process = subprocess.Popen(
    [".venv/bin/uvicorn", "app.api.main:app", "--host", "127.0.0.1", "--port", "8000"],
    stdout=open("uvicorn.log", "w"),
    stderr=subprocess.STDOUT,
    text=True
)

if not wait_for_port(8000, timeout=60):
    server_process.kill()
    exit(1)

queries = [
    "What are the important things I should study from this?",
    "Tell me everything important about PV modules.",
    "How are the different concepts in this module connected?",
    "What does this document say about efficiency?"
]

for q in queries:
    print(f"\n====================\nQUERY: {q}")
    payload = {
        "query": q,
        "top_k": 5,
        "filename": "BME654B-module-2-pdf.pdf"
    }
    t_start = time.perf_counter()
    response = requests.post("http://127.0.0.1:8000/questions", json=payload, timeout=300)
    t_end = time.perf_counter()
    
    data = response.json()
    print(f"LATENCY: {t_end - t_start:.2f}s")
    
    if "retrieved_chunks" in data:
        ctx = data["retrieved_chunks"]
        print(f"CONTEXT SIZE: {len(ctx)} chunks")
        for c in ctx:
            cid = c.get("chunk_id", "?")
            head = c.get("heading", "None")
            struct = c.get("is_structural", False)
            print(f"  - Chunk {cid} | Structural: {struct} | Heading: {head}")
    
    print(f"\nANSWER:\n{data.get('answer', 'ERROR')}")

server_process.kill()
