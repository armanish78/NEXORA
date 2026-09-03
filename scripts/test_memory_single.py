import requests
import time
import subprocess
import psutil
import socket

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

# Start uvicorn
server_process = subprocess.Popen(
    [".venv/bin/uvicorn", "app.api.main:app", "--host", "127.0.0.1", "--port", "8000"],
    stdout=open("uvicorn.log", "w"),
    stderr=subprocess.STDOUT,
    text=True
)

if not wait_for_port(8000, timeout=60):
    server_process.kill()
    exit(1)

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
server_alive = server_process.poll() is None
server_process.kill()

print("RESULTS")
print("-------")
print(f"Total latency: {total_time:.2f} s")
print(f"Peak VRAM: {vram_peak:.1f} MB")
print(f"Application alive: {'yes' if server_alive else 'no'}")

# Count instances
with open("uvicorn.log", "r") as f:
    logs = f.read()

count = logs.count("[DEBUG] INSTANTIATING SENTENCETRANSFORMER!")
print(f"SentenceTransformer instances created: {count}")
