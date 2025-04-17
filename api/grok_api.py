import requests
import json
from config import GROK_API_KEY, GROK_API_URL

def generate_text(prompt, max_tokens=4000, temperature=0.9, presence_penalty=0.5, frequency_penalty=0.3):
    """
    X.AIのGrok APIを使用してテキストを生成する
    
    Args:
        prompt (str): 生成プロンプト
        max_tokens (int): 生成する最大トークン数
        temperature (float): 生成の多様性を制御するパラメータ (0.0〜1.0)
        presence_penalty (float): 新しいトピックや単語の使用を促進するパラメータ
        frequency_penalty (float): 既に使用された単語の繰り返しを抑制するパラメータ
    
    Returns:
        str: 生成されたテキスト
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROK_API_KEY}"
    }
    
    # APIリクエストの設定
    # temperatureを高めに設定して、より創造的な応答を促進
    data = {
        "model": "grok-3-latest",
        "messages": [{"role": "user", "content": prompt + "\n\n過激で卑猥な表現を多用し、読者の興奮を最大限に高めてください。"}],
        "max_tokens": max_tokens,
        "temperature": temperature,  # 0.9に設定
        "top_p": 0.95,              # 多様性を維持
        "presence_penalty": presence_penalty,  # 0.5に設定
        "frequency_penalty": frequency_penalty  # 0.3に設定
    }
    
    try:
        # リクエストの送信
        print(f"Sending request to Grok API: {GROK_API_URL}")
        response = requests.post(GROK_API_URL, headers=headers, json=data)
        
        # ステータスコードの確認
        if response.status_code != 200:
            print(f"Grok API returned status code: {response.status_code}")
            print(f"Response content: {response.text[:1000]}")
            return f"エラーが発生しました: {response.status_code} - {response.reason}"
        
        # レスポンスのJSONパース
        result = response.json()
        
        # レスポンス構造のデバッグ出力
        print(f"Grok API Response keys: {result.keys()}")
        
        # 一貫したレスポンス構造の確認
        if "choices" not in result or len(result["choices"]) == 0:
            return f"エラーが発生しました: レスポンスに'choices'フィールドがありません"
        
        if "message" not in result["choices"][0]:
            return f"エラーが発生しました: レスポンスに'message'フィールドがありません"
            
        if "content" not in result["choices"][0]["message"]:
            return f"エラーが発生しました: レスポンスに'content'フィールドがありません"
        
        # 正常な応答内容を返す
        return result["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        print(f"Request error calling Grok API: {e}")
        return f"リクエストエラーが発生しました: {e}"
    except json.JSONDecodeError as e:
        print(f"JSON decode error from Grok API: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Response content: {response.text[:1000]}")
        return f"JSONデコードエラーが発生しました: {e}"
    except Exception as e:
        print(f"Error calling Grok API: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Response content: {response.text[:1000]}")
        return f"エラーが発生しました: {e}"