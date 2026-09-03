with open("/home/nova/Desktop/RAG/tests/test_document_scoping.py", "r") as f:
    content = f.read()

content = content.replace(
    'has_outline = any(res.get("is_structural") for res in results)',
    'print(f"\\n\\nRESULTS LEN: {len(results)}\\nRESULTS: {results}\\n\\n"); has_outline = any(res.get("is_structural") for res in results)'
)

with open("/home/nova/Desktop/RAG/tests/test_document_scoping.py", "w") as f:
    f.write(content)
