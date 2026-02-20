import sys
import json
import requests
import tempfile
import os

sys.path.insert(0, 'src')

url = 'http://localhost:11434/api/chat'
payload = {
    'model': 'qwen2.5:3b',
    'messages': [{'role': 'user', 'content': '你好'}],
    'stream': False
}

response = requests.post(url, json=payload, timeout=30)
result = json.loads(response.content)
content = result.get("message", {}).get("content", "")

# 写入临时文件再读取，修复Windows编码问题
with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
    f.write(content)
    temp_path = f.name

try:
    with open(temp_path, 'r', encoding='utf-8') as f:
        fixed_content = f.read()
    print('Fixed content:', fixed_content)
finally:
    os.unlink(temp_path)
