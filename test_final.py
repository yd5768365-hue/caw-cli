import sys
import json
import requests

sys.path.insert(0, 'src')

url = 'http://localhost:11434/api/chat'
payload = {
    'model': 'qwen2.5:3b',
    'messages': [{'role': 'user', 'content': '你好'}],
    'stream': False
}

json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
response = requests.post(
    url, 
    data=json_data,
    timeout=30,
    headers={"Content-Type": "application/json; charset=utf-8"}
)
text = response.content.decode('utf-8')
result = json.loads(text)
content = result.get("message", {}).get("content", "")
print('Content:', content)
