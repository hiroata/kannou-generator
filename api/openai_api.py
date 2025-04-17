from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

def generate_text(prompt, max_tokens=2000, temperature=0.7):
    """
    OpenAI API (GPT-4)を使用してテキストを生成する
    
    Args:
        prompt (str): 生成プロンプト
        max_tokens (int): 生成する最大トークン数
        temperature (float): 生成の多様性を制御するパラメータ
    
    Returns:
        str: 生成されたテキスト
    """
    try:
        # OpenAI Clientの初期化
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # チャット完了リクエストの送信
        response = client.chat.completions.create(
            model=OPENAI_MODEL,  # "gpt-4.1" が使用される
            messages=[
                {"role": "system", "content": "あなたは18禁官能小説の執筆を得意とする小説家です。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # レスポンスから生成されたテキストを抽出
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return f"エラーが発生しました: {e}"