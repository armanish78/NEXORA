import requests
import json

base_url = "http://127.0.0.1:8000"

# 1. Fetch available document to test
import sqlite3
conn = sqlite3.connect("nexora.db")
c = conn.cursor()
try:
    c.execute("SELECT filename FROM document_metadata LIMIT 1")
    row = c.fetchone()
    if row:
        doc_filename = row[0]
    else:
        # Fallback to test document name if db fails
        doc_filename = "test.pdf"
except Exception as e:
    print(f"DB Error: {e}")
    doc_filename = "test.pdf"
conn.close()

print(f"Selected document: {doc_filename}")

# 2. Fetch topics for that document
try:
    topics_url = f"{base_url}/documents/{doc_filename}/topics"
    res = requests.get(topics_url)
    topics = res.json().get('topics', [])
    print(f"Fetched topics: {topics}")
except Exception as e:
    print(f"Topics Error: {e}")
    topics = ["SAMPLE_TOPIC"]

if not topics:
    topics = ["SAMPLE_TOPIC"]

specific_topic = topics[0]

# 3. Simulate frontend createQuiz payload for Specific Topic
payload_specific = {
    "topic": specific_topic,
    "difficulty": "medium",
    "num_questions": 5,
    "filename": doc_filename
}

print("\n### SPECIFIC TOPIC TRACE")
print(f"Request JSON: {json.dumps(payload_specific, indent=2)}")

res_spec = requests.post(f"{base_url}/quizzes", json=payload_specific)
print(f"HTTP Status: {res_spec.status_code}")
print(f"Response: {res_spec.text}")


# 4. Simulate frontend createQuiz payload for All Topics
payload_all = {
    "topic": "All Topics",
    "difficulty": "medium",
    "num_questions": 5,
    "filename": doc_filename
}

print("\n### ALL TOPICS TRACE")
print(f"Request JSON: {json.dumps(payload_all, indent=2)}")

res_all = requests.post(f"{base_url}/quizzes", json=payload_all)
print(f"HTTP Status: {res_all.status_code}")
print(f"Response: {res_all.text}")

