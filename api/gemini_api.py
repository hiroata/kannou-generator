from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

def generate_text(prompt, max_tokens=2000, temperature=0.7):
    try:
        # Clientオブジェクトの初期化
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # 生成設定を別のオブジェクトとして準備
        config = genai.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature
        )
        
        # レスポンス生成
        response = client.generate_content(
            model=GEMINI_MODEL,  # "gemini-2.5-pro-preview-03-25" が使用される
            contents=prompt,
            generation_config=config
        )
        
        # レスポンステキストを返す
        return response.text
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return f"エラーが発生しました: {e}"