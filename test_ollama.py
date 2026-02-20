import sys
import json
import requests

url = 'http://localhost:11434/api/chat'
messages = [{'role': 'user', 'content': '你好'}]

payload = {
    'model': 'qwen2.5:3b',
    'messages': messages,
    'stream': False
}

print("Testing Ollama API...")
try:
    response = requests.post(
        url, 
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
        timeout=30,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Raw result: {result}")
    if "message" in result and "content" in result["message"]:
        print(f"Content: {result['message']['content']}")
except Exception as e:
    print(f"Error: {e}")
