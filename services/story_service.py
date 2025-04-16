import os
import json
import uuid
from api import grok_api, gemini_api
from services import setting_service, synopsis_service
from config import WRITING_STYLES

def generate_story(synopsis_id, synopsis_index=0, model="gemini", style="murakami", chapter=1):
    """
    あらすじに基づいて小説を生成する
    
    Args:
        synopsis_id (str): あらすじID
        synopsis_index (int): あらすじのインデックス
        model (str): 使用するモデル ('grok' または 'gemini')
        style (str): 文体スタイル ('murakami' または 'dan')
        chapter (int): 生成する章番号
    
    Returns:
        dict: 生成された小説
    """
    # あらすじの読み込み
    synopses_data = synopsis_service.load_synopsis(synopsis_id)
    if not synopses_data:
        return {"error": "あらすじが見つかりません"}
    
    # 設定の読み込み
    setting_id = synopses_data.get("setting_id")
    setting_data = setting_service.load_setting(setting_id)
    
    # 選択されたあらすじ
    selected_synopsis = synopses_data.get("synopses", [])[synopsis_index]
    
    # 文体の選択
    writing_style = WRITING_STYLES.get(style, WRITING_STYLES["murakami"])
    
    # 章に応じたプロンプトの作成
    if chapter == 1:
        story_part = "導入部。物語を設定し、登場人物を紹介し、初期の性的緊張を確立します。"
    elif chapter == 2:
        story_part = "展開部。性的緊張が高まり、関係性が深まり、官能的なシーンが展開します。"
    elif chapter == 3:
        story_part = "クライマックスと結末。物語のピークとなる官能シーンと、その後の展開を描写します。"
    else:
        story_part = "追加エピソード。メインストーリーに追加される官能的なエピソードです。"
    
    prompt = f"""
    あなたは官能小説の作家です。以下の設定とあらすじに基づいて、{writing_style}で小説の第{chapter}章を書いてください。
    これは{story_part}
    
    設定:
    {json.dumps(setting_data, ensure_ascii=False)}
    
    あらすじ:
    {json.dumps(selected_synopsis, ensure_ascii=False)}
    
    小説は約2000-3000文字で、以下の点に注意してください：
    - 官能的な描写は詳細に
    - 臨場感のある会話と心理描写
    - 読者を引き込む展開
    - 選択した文体の特徴を強く反映させる
    
    章のタイトルをつけて、小説を執筆してください。
    """
    
    # モデル選択
    if model.lower() == "grok":
        story_text = grok_api.generate_text(prompt, max_tokens=3000)
    else:
        story_text = gemini_api.generate_text(prompt, max_tokens=3000)
    
    # 小説の保存
    story_id = str(uuid.uuid4())
    save_story(story_id, {
        "setting_id": setting_id,
        "synopsis_id": synopsis_id,
        "synopsis_index": synopsis_index,
        "chapter": chapter,
        "style": style,
        "model": model,
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