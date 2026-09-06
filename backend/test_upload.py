from fastapi.testclient import TestClient
from app.api.main import app
import json

with TestClient(app) as client:
    with open('data/raw/BIS613D-module-3-pdf.pdf', 'rb') as f:
        response = client.post(
            "/documents",
            files={"file": ("nexora_test_solar.pdf", f, "application/pdf")}
        )

    print("Upload Response:", response.json())

    # Check topics
    topics_resp = client.get("/documents/nexora_test_solar.pdf/topics")
    print("Topics Response:", topics_resp.json())

