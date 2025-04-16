import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# API設定
GROK_API_KEY = os.getenv("GROK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# API URL設定
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-preview-03-25:generateContent"

# モデル設定
GROK_MODEL = "grok-3-latest"
GEMINI_MODEL = "gemini-2.5-pro-preview-03-25"

# 文体設定
WRITING_STYLES = {
    "murakami": "村上龍のような都会的で生々しい描写と冷静な語り口、直接的な性描写とシニカルな観察眼が特徴的な文体",
    "dan": "団鬼六のようなSM描写に特化した、緊張感と支配・服従関係を詳細に描写する文体"
}