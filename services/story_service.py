import os
import json
import uuid
from api import grok_api
from services import setting_service, synopsis_service
from config import WRITING_STYLES

def generate_story(synopsis_id, synopsis_index=0, model="grok", style="murakami", chapter=1, direction="", enhance_options=None):
    """
    あらすじに基づいて小説を生成する
    
    Args:
        synopsis_id (str): あらすじID
        synopsis_index (int): あらすじのインデックス
        model (str): 使用するモデル ('grok' のみサポート)
        style (str): 文体スタイル ('murakami' または 'dan')
        chapter (int): 生成する章番号
        direction (str): 次の章の方向性に関する指示（オプション）
        enhance_options (dict): 強化オプション
            - enhance_psychology (bool): キャラクター心理の強化
            - enhance_emotions (bool): 感情の起伏の強化
            - enhance_sensory (bool): 五感表現の強化
            - enhance_voice (bool): キャラクターの声の一貫化
            - add_psychological_themes (bool): 心理的テーマの追加
            - explicitness_level (int): 露骨さレベル (1-5)
    
    Returns:
        dict: 生成された小説
    """
    # デフォルトの強化オプション
    if enhance_options is None:
        enhance_options = {
            "enhance_psychology": True,
            "enhance_emotions": True,
            "enhance_sensory": True,
            "enhance_voice": True,
            "add_psychological_themes": False,
            "explicitness_level": 3
        }
    
    # モデルの強制
    model = "grok"  # 現在はgrokのみサポート
    
    # あらすじの読み込み
    synopses_data = synopsis_service.load_synopsis(synopsis_id)
    if not synopses_data:
        return {"error": "あらすじが見つかりません"}
    
    # 設定の読み込み
    setting_id = synopses_data.get("setting_id")
    setting_data = setting_service.load_setting(setting_id)
    
    # 選択されたあらすじ
    synopses = synopses_data.get("synopses", [])
    
    # あらすじが存在し、インデックスが範囲内かチェック
    if not isinstance(synopses, list) or synopsis_index >= len(synopses):
        return {"error": "指定されたあらすじが存在しません"}
        
    selected_synopsis = synopses[synopsis_index]
    
    # 文体の選択
    writing_style = WRITING_STYLES.get(style, WRITING_STYLES["murakami"])
    
    # 章に応じたプロンプトの作成
    if chapter == 1:
        story_part = "導入部。物語を設定し、登場人物を紹介し、初期の性的緊張を確立します。"
        target_length = "700文字から1000文字"
    elif chapter == 2:
        story_part = "展開部。性的緊張が高まり、関係性が深まり、官能的なシーンが展開します。"
        target_length = "700文字から1000文字"
    elif chapter == 3:
        story_part = "クライマックスと結末。物語のピークとなる官能シーンと、その後の展開を描写します。"
        target_length = "800文字から1200文字"
    else:
        story_part = "追加エピソード。メインストーリーに追加される官能的なエピソードです。"
        target_length = "800文字から1200文字"
    
    # 露骨さレベルの説明
    explicitness_level = enhance_options.get("explicitness_level", 3)
    explicitness_descriptions = {
        1: "非常に控えめで文学的。性的な内容は主に比喩と象徴で表現。直接的な性表現はほとんど使わず、文学的表現に終始。",
        2: "控えめながら暗示的。性的内容は主に比喩的表現を用い、直接的表現は最小限。情緒的・心理的描写を重視。",
        3: "バランスの取れた表現。性的内容は比較的直接的に描写されるが、文学的表現と組み合わせる。",
        4: "より直接的。性的表現は遠慮なく描写されるが、文学的比喩も使用。登場人物の内面描写と肉体描写のバランスを保つ。",
        5: "強烈で生々しい表現。性的内容は非常に直接的かつ詳細に描写される。村上龍風の都会的で冷たい視線と生々しい描写。"
    }
    
    explicitness_instruction = explicitness_descriptions.get(explicitness_level, explicitness_descriptions[3])
    
    # 前章からの方向性が指定されているかチェック
    direction_instruction = ""
    if direction:
        direction_instruction = f"""
        【重要】以下のユーザーからの指示に従って内容を展開してください：
        {direction}
        """
    
    # 文学的表現強化の指示
    literary_instruction = """
    【文学的表現と表記について重要な指示】
    1. 登場人物の年齢を直接表記しないでください。代わりに経験や立場、外見的特徴から推測させる表現を使ってください。
    2. バストサイズや性器のサイズなど、数値的な身体描写は避けてください。代わりに比喩や感覚的表現、文学的な描写を用いてください。
    3. 村上龍のようなハードボイルドで冷静な観察眼と、徹底的な描写で読者の想像力を刺激してください。
    4. 性的描写においても文学性を保ち、露骨でありながらも芸術的な表現を心がけてください。
    5. 登場人物の内面と外面の乖離、都会の孤独感、人間関係の空虚さなどのテーマを織り込んでください。
    6. 性行為を単なる肉体的行為としてではなく、心理的・象徴的な意味合いを持つ出来事として描写してください。
    """
    
    prompt = f"""
    あなたは18禁官能小説の作家です。以下の設定とあらすじに基づいて、{writing_style}で小説の第{chapter}章を書いてください。
    これは{story_part}
    
    設定:
    {json.dumps(setting_data, ensure_ascii=False)}
    
    あらすじ:
    {json.dumps(selected_synopsis, ensure_ascii=False)}
    
    {direction_instruction}
    
    {literary_instruction}
    
    表現の露骨さレベル: {explicitness_level}
    表現の指針: {explicitness_instruction}
    
    小説は{target_length}程度で、以下の点に注意してください：
    1. 官能的な描写は詳細かつ生々しく、しかし同時に文学的表現を重視する。
    2. 登場人物の会話には「あぁん」「んっ」などの喘ぎ声や卑猥な言葉を盛り込むが、露骨さのレベルに応じて調整する。
    3. キャラクターの心理描写と身体的な反応を鮮明に表現する。
    4. 臨場感のある会話と性的な緊張感を醸成する。
    5. 読者を引き込む官能的な展開を心がける。
    6. 選択した文体の特徴を強く反映させる。
    7. 年齢や具体的サイズの直接表記は避け、代わりに文学的表現を用いる。
    
    章のタイトルをつけて、小説を執筆してください。改行を適切に使用し、読みやすくしてください。
    """
    
    # Grok API呼び出し（temperatureを上げて創造性を高める）
    story_text = grok_api.generate_text(prompt, max_tokens=4000, temperature=0.8)
    
    # エラーチェック
    if story_text.startswith("エラーが発生しました"):
        return {"error": story_text, "chapter": chapter}
    
    # 小説の保存
    story_id = str(uuid.uuid4())
    save_story(story_id, {
        "setting_id": setting_id,
        "synopsis_id": synopsis_id,
        "synopsis_index": synopsis_index,
        "chapter": chapter,
        "style": style,
        "model": model,
        "direction": direction,
        "enhance_options": enhance_options,
        "text": story_text
    })
    
    return {
        "id": story_id,
        "chapter": chapter,
        "text": story_text
    }

def save_story(story_id, story_data):
    """小説をファイルに保存する"""
    filepath = os.path.join("data", "stories", f"{story_id}.json")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(story_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def load_story(story_id):
    """小説をファイルから読み込む"""
    filepath = os.path.join("data", "stories", f"{story_id}.json")
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        story_data = json.load(f)
    
    return story_data