import os
import json
import uuid
from api import grok_api
from services import setting_service, synopsis_service
from config import WRITING_STYLES

def generate_story(synopsis_id, synopsis_index=0, model="grok", style="murakami", chapter=1, direction=""):
    """
    あらすじに基づいて小説を生成する
    
    Args:
        synopsis_id (str): あらすじID
        synopsis_index (int): あらすじのインデックス
        model (str): 使用するモデル ('grok' のみサポート)
        style (str): 文体スタイル ('murakami' または 'dan')
        chapter (int): 生成する章番号
        direction (str): 次の章の方向性に関する指示（オプション）
    
    Returns:
        dict: 生成された小説
    """
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
    
    # 前章からの方向性が指定されているかチェック
    direction_instruction = ""
    if direction:
        direction_instruction = f"""
        【重要】以下のユーザーからの指示に従って内容を展開してください：
        {direction}
        """
    
    prompt = f"""
    あなたは18禁官能小説の作家です。以下の設定とあらすじに基づいて、{writing_style}で小説の第{chapter}章を書いてください。
    これは{story_part}
    
    設定:
    {json.dumps(setting_data, ensure_ascii=False)}
    
    あらすじ:
    {json.dumps(selected_synopsis, ensure_ascii=False)}
    
    {direction_instruction}
    
    小説は{target_length}程度で、以下の点に注意してください：
    1. 官能的な描写は非常に詳細かつ直接的に。性器の名称や卑猥な表現を遠慮なく使用する。
    2. 登場人物の会話には「あぁん」「んっ」などの喘ぎ声や「おまんこ」「ちんぽ」などの淫語を積極的に盛り込む。
    3. キャラクターの心理描写と身体的な反応を鮮明に表現する。
    4. 臨場感のある会話と性的な緊張感を醸成する。
    5. 読者を引き込む官能的な展開を心がける。
    6. 選択した文体の特徴を強く反映させる。
    7. 日本の成人向け同人誌のような過激で露骨な性描写を含める。
    
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