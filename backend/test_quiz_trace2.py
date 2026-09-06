import urllib.request
import json
import ssl

base_url = "http://127.0.0.1:8000"
doc_filename = "test.pdf"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, context=ctx) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
        
def get(url):
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, context=ctx) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

_, topics_data = get(f"{base_url}/documents/{doc_filename}/topics")
topics = topics_data.get("topics", [])
print(f"Fetched topics length: {len(topics)}")
print(f"Sample topics: {topics[:3]}")

# 2. All Topics Quiz
payload_all = {
    "topic": "All Topics",
    "difficulty": "medium",
    "num_questions": 5,
    "filename": doc_filename
}
status, res_all = post(f"{base_url}/quizzes", payload_all)
print(f"ALL TOPICS HTTP Status: {status}")
print(f"ALL TOPICS Response success: {res_all.get('success')}")

# 3. Specific Topic Quiz
if topics:
    payload_specific = {
        "topic": topics[0],
        "difficulty": "medium",
        "num_questions": 5,
        "filename": doc_filename
    }
    status, res_spec = post(f"{base_url}/quizzes", payload_specific)
    print(f"SPECIFIC TOPIC HTTP Status: {status}")
    print(f"SPECIFIC TOPIC Response success: {res_spec.get('success')}")
