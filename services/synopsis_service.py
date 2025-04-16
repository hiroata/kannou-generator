import os
import json
import uuid
from api import grok_api, gemini_api
from services import setting_service
from config import WRITING_STYLES

def generate_synopses(setting_id, model="gemini", style="murakami", num_synopses=3):
    """
    設定に基づいてあらすじを生成する
    
    Args:
        setting_id (str): 設定ID
        model (str): 使用するモデル ('grok' または 'gemini')
        style (str): 文体スタイル ('murakami' または 'dan')
        num_synopses (int): 生成するあらすじの数
    
    Returns:
        list: 生成されたあらすじのリスト
    """
    # 設定の読み込み
    setting_data = setting_service.load_setting(setting_id)
    if not setting_data:
        return {"error": "設定が見つかりません"}
    
    # 文体の選択
    writing_style = WRITING_STYLES.get(style, WRITING_STYLES["murakami"])
    
    prompt = f"""
    あなたは官能小説のあらすじジェネレーターです。以下の設定に基づいて、{writing_style}で{num_synopses}つのあらすじを作成してください。
    
    設定:
    {json.dumps(setting_data, ensure_ascii=False)}
    
    各あらすじには以下を含めてください:
    - タイトル
    - 導入部（どのように物語が始まるか）
    - 展開（性的緊張が高まる部分）
    - クライマックス（物語の頂点）
    - 結末（どのように物語が終わるか）
    
    レスポンスはJSON形式で提供してください。
    """
    
    # モデル選択
    if model.lower() == "grok":
        response = grok_api.generate_text(prompt)
    else:
        response = gemini_api.generate_text(prompt)
    
    # JSONパース（エラー処理）
    try:
        synopses_data = json.loads(response)
    except:
        # JSONでない場合、簡易的な構造を作成
        synopses_data = {"error": "正しい形式で取得できませんでした", "raw_response": response}
    
    # あらすじの保存
    synopsis_id = str(uuid.uuid4())
    save_synopsis(synopsis_id, synopses_data, setting_id)
    
    return {"id": synopsis_id, "synopses": synopses_data}

def save_synopsis(synopsis_id, synopses_data, setting_id):
    """あらすじをファイルに保存する"""
    filepath = os.path.join("data", "synopses", f"{synopsis_id}.json")
    
    # 設定IDを含める
    data = {
        "setting_id": setting_id,
        "synopses": synopses_data
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filepath

def load_synopsis(synopsis_id):
    """あらすじをファイルから読み込む"""
    filepath = os.path.join("data", "synopses", f"{synopsis_id}.json")
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        synopses_data = json.load(f)
    
    return synopses_data