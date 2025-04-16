import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# API設定
GROK_API_KEY = os.getenv("GROK_API_KEY")

# API URL設定
GROK_API_URL = "https://api.x.ai/v1/chat/completions"

# モデル設定
GROK_MODEL = "grok-3-latest"

# 文体設定
WRITING_STYLES = {
    "murakami": "村上龍のような都会的で生々しい描写と冷静な語り口、直接的かつ露骨な性描写とシニカルな観察眼が特徴的な文体。登場人物の会話には卑猥な言葉や性器を表す淫語を積極的に盛り込み、喘ぎ声や乱れた息遣いも「あぁん」「くぅっ」などと直接的に表現する。",
    "dan": "団鬼六のようなSM描写に特化した、緊張感と支配・服従関係を詳細に描写する文体。性的な快感と痛みの混じり合う感覚を赤裸々に表現し、「おまんこ」「ちんぽ」などの淫語を多用。命令口調や支配的・服従的なセリフ、激しい喘ぎ声を多く含み、官能的な情景をより生々しく描写する。"
}