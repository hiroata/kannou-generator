import requests
import json
from config import GROK_API_KEY, GROK_API_URL

def generate_text(prompt, max_tokens=2000):
    """
    X.AIのGrok APIを使用してテキストを生成する
    
    Args:
        prompt (str): 生成プロンプト
        max_tokens (int): 生成する最大トークン数
    
    Returns:
        str: 生成されたテキスト
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROK_API_KEY}"
    }
    
    data = {
        "model": "grok-3-latest",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7  # 追加
    }
    
    try:
        # jsonパラメータを使用（dataではなく）
        response = requests.post(GROK_API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        print(f"Grok API Response keys: {result.keys()}")
        
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error calling Grok API: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Response content: {response.text[:500]}")
        return f"エラーが発生しました: {e}"