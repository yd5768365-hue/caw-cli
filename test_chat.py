#!/usr/bin/env python
"""测试学习模式"""
import sys
sys.path.insert(0, 'src')

import requests
import json

url = 'http://localhost:11434/api/chat'

def test_chat():
    payload = {
        'model': 'qwen2.5:3b',
        'messages': [{'role': 'user', 'content': '你好'}],
        'stream': False
    }
    
    print("Testing...")
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        # 关键修复：手动UTF-8解码
        text = response.content.decode('utf-8')
        result = json.loads(text)
        content = result.get("message", {}).get("content", "")
        print(f"Response: {content}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chat()
