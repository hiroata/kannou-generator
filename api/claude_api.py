from anthropic import Anthropic
from config import CLAUDE_API_KEY, CLAUDE_MODEL

def generate_text(prompt, max_tokens=2000, temperature=0.7):
    """
    Anthropic Claude APIを使用してテキストを生成する
    
    Args:
        prompt (str): 生成プロンプト
        max_tokens (int): 生成する最大トークン数
        temperature (float): 生成の多様性を制御するパラメータ
    
    Returns:
        str: 生成されたテキスト
    """
    try:
        # Anthropic Clientの初期化
        client = Anthropic(api_key=CLAUDE_API_KEY)
        
        # メッセージ作成リクエストの送信
        response = client.messages.create(
            model=CLAUDE_MODEL,  # "claude-3-7-sonnet-20250219" が使用される
            max_tokens=max_tokens,
            temperature=temperature,
            system="あなたは18禁官能小説の執筆を得意とする小説家です。日本語で詳細で文学的な性描写を行うことができます。",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # レスポンスから生成されたテキストを抽出
        return response.content[0].text
        
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        return f"エラーが発生しました: {e}"