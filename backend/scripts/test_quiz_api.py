import requests
import json

URL = "http://127.0.0.1:8000/quizzes"

# 1. Correct document
req1 = {
    "user_id": 1,
    "topic": "Cloud Computing and Virtualized Datacenters",
    "difficulty": "easy",
    "num_questions": 1,
    "filename": "BIS613D-module-3-pdf.pdf"
}
res1 = requests.post(URL, json=req1)
print("Correct doc:", res1.status_code, res1.text)
