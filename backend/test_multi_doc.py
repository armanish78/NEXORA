import requests

with open("doc_A.txt", "w") as f: f.write("This is document A.\n" * 10)
with open("doc_B.txt", "w") as f: f.write("This is document B.\n" * 10)

def upload(filename):
    with open(filename, "rb") as f:
        res = requests.post("http://127.0.0.1:8000/documents", files={"file": f})
    print(f"Uploaded {filename}: {res.json()}")

def check_topics(filename):
    res = requests.get(f"http://127.0.0.1:8000/documents/{filename}/topics")
    print(f"Topics for {filename}: {res.json()}")

import subprocess
import time

print("Starting server...")
p = subprocess.Popen(["python", "-m", "uvicorn", "app.api.main:app", "--host", "127.0.0.1", "--port", "8000"])
time.sleep(4)

try:
    upload("doc_A.txt")
    check_topics("doc_A.txt")
    check_topics("doc_B.txt")
    
    upload("doc_B.txt")
    check_topics("doc_A.txt")
    check_topics("doc_B.txt")
finally:
    p.terminate()
