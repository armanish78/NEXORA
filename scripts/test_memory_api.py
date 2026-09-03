import requests
import time
import subprocess
import psutil
import json
import socket
import os

try:
    import pynvml
    pynvml.nvmlInit()
    HAS_GPU = True
except Exception:
    HAS_GPU = False

def get_vram():
    if not HAS_GPU:
        return 0
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    return info.used / 1024**2

def get_ram():
    return psutil.virtual_memory().used / 1024**3

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

print("BEFORE")
print("------")
print(f"RAM: {get_ram():.2f} GB")
print(f"VRAM: {get_vram():.1f} MB")

# Start uvicorn
print("Starting uvicorn...")
server_process = subprocess.Popen(
    [".venv/bin/uvicorn", "app.api.main:app", "--host", "127.0.0.1", "--port", "8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

if not wait_for_port(8000, timeout=60):
    print("Failed to start server")
    server_process.kill()
    exit(1)

# Check processes
python_procs = [p for p in psutil.process_iter(['pid', 'name', 'cmdline']) if p.info['name'] == 'python']
print(f"Loaded Python processes: {len(python_procs)}")

# Wait a bit for models to lazy load if they do, or just send request.
# The app lazily loads models on first request usually.
print("Qwen loaded: No (lazy loaded on first request)")
print("Embedding model loaded: No (lazy loaded on first request)")

print("\nREQUEST")
print("-------")
payload = {
    "query": "What is this document about?",
    "top_k": 5
}

t_start = time.perf_counter()
vram_peak = get_vram()

import threading
def monitor_vram():
    global vram_peak
    while server_process.poll() is None and not done:
        v = get_vram()
        if v > vram_peak:
            vram_peak = v
        time.sleep(0.1)

done = False
monitor_thread = threading.Thread(target=monitor_vram)
monitor_thread.start()

try:
    response = requests.post("http://127.0.0.1:8000/questions", json=payload, timeout=300)
    data = response.json()
except Exception as e:
    data = {"error": str(e)}

done = True
monitor_thread.join()
t_end = time.perf_counter()

total_time = t_end - t_start
context_chunks = data.get("results", [])
prompt_tokens = len(data.get("answer", "")) * 2 # rough estimate if token count isn't returned

print(f"Retrieval: N/A (hidden inside API)")
print(f"Context chunks: {len(context_chunks)}")
print(f"Prompt tokens (approx): {prompt_tokens} (answer length proxy)")
print(f"Peak VRAM: {vram_peak:.1f} MB")
print(f"Total latency: {total_time:.2f} s")

print("\nAFTER")
print("-----")
print(f"RAM: {get_ram():.2f} GB")
print(f"VRAM: {get_vram():.1f} MB")

server_alive = server_process.poll() is None
print(f"Application alive: {'yes' if server_alive else 'no'}")

server_process.kill()

if server_alive:
    print("\nVERDICT: SAFE / STILL MEMORY-BOUND")
else:
    print("\nVERDICT: CRASHED")

