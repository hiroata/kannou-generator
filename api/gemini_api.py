from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

def generate_text(prompt, max_tokens=2000):
    """
    Google Gemini APIを使用してテキストを生成する（最新のSDK使用）
    
    Args:
        prompt (str): 生成プロンプト
        max_tokens (int): 生成する最大トークン数
    
    Returns:
        str: 生成されたテキスト
    """
    try:
        # Clientオブジェクトの初期化
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # レスポンス生成
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": 0.7
            }
        )
        
        # レスポンステキストを返す
        return response.text
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return f"エラーが発生しました: {e}"