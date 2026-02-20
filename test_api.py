import requests
import json
import sys

url = 'http://localhost:11434/api/chat'
payload = {
    'model': 'qwen2.5:3b',
    'messages': [{'role': 'user', 'content': '你好'}],
    'stream': False
}

print("Sending request...", file=sys.stderr)
try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status: {response.status_code}", file=sys.stderr)
    text = response.content.decode('utf-8')
    result = json.loads(text)
    content = result.get("message", {}).get("content", "")
    print(f"Content: {content}", file=sys.stderr)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
