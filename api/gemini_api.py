import requests
import json
from config import GEMINI_API_KEY, GEMINI_API_URL

def generate_text(prompt, max_tokens=4000, temperature=0.9, presence_penalty=0.5, frequency_penalty=0.3):
    """
    Google Geminiモデルを使用してテキストを生成する
    
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
        "Authorization": f"Bearer {GEMINI_API_KEY}"
    }
    
    # APIリクエストの設定
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt + "\n\n過激で卑猥な表現を多用し、読者の興奮を最大限に高めてください。"
                    }
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
            "topP": 0.95,
            "topK": 40
        }
    }
    
    try:
        # リクエストの送信
        print(f"Sending request to Gemini API: {GEMINI_API_URL}")
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        
        # ステータスコードの確認
        if response.status_code != 200:
            print(f"Gemini API returned status code: {response.status_code}")
            print(f"Response content: {response.text[:1000]}")
            return f"エラーが発生しました: {response.status_code} - {response.reason}"
        
        # レスポンスのJSONパース
        result = response.json()
        
        # レスポンス構造のデバッグ出力
        print(f"Gemini API Response keys: {result.keys()}")
        
        # Gemini API のレスポンス構造に基づいてテキストを抽出
        if "candidates" in result and len(result["candidates"]) > 0:
            candidate = result["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                parts = candidate["content"]["parts"]
                if parts and "text" in parts[0]:
                    return parts[0]["text"]
            
        return f"エラーが発生しました: 期待するレスポンス形式ではありません"
        
    except requests.exceptions.RequestException as e:
        print(f"Request error calling Gemini API: {e}")
        return f"リクエストエラーが発生しました: {e}"
    except json.JSONDecodeError as e:
        print(f"JSON decode error from Gemini API: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Response content: {response.text[:1000]}")
        return f"JSONデコードエラーが発生しました: {e}"
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Response content: {response.text[:1000]}")
        return f"エラーが発生しました: {e}"