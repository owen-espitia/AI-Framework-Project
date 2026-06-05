import requests
response = requests.post(
    "http://localhost:12434/engines/v1/chat/completions",
    json={
        "model": "ai/smollm2",
        "messages": [{"role": "user", "content": "Explain what Docker is in one sentence."}]
    }
)
print(response.json())
