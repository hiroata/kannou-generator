import os
import json
import uuid
from api import grok_api, gemini_api
from config import WRITING_STYLES

def generate_setting(model="gemini", setting_type="一般", additional_details=""):
    """
    小説の設定を生成する
    
    Args:
        model (str): 使用するモデル ('grok' または 'gemini')
        setting_type (str): 設定のタイプ
        additional_details (str): 追加の詳細
    
    Returns:
        dict: 生成された設定
    """
    prompt = f"""
    あなたは官能小説の設定ジェネレーターです。以下の条件で魅力的な設定を作成してください。
    
    タイプ: {setting_type}
    追加情報: {additional_details}
    
    以下の内容を含めてください:
    - 登場人物（名前、年齢、身体的特徴、性格）を3-5人
    - 舞台設定（場所、時代）
    - 背景状況（どのような関係性にあるか）
    
    レスポンスはJSON形式で提供してください。
    """
    
    # モデル選択
    if model.lower() == "grok":
        response = grok_api.generate_text(prompt)
    else:
        response = gemini_api.generate_text(prompt)
    
    # JSONパース（エラー処理）
    try:
        setting_data = json.loads(response)
    except:
        # JSONでない場合、簡易的な構造を作成
        setting_data = {"error": "正しい形式で取得できませんでした", "raw_response": response}
    
    # 設定の保存
    setting_id = str(uuid.uuid4())
    save_setting(setting_id, setting_data)
    
    return {"id": setting_id, "setting": setting_data}

def save_setting(setting_id, setting_data):
    """設定をファイルに保存する"""
    filepath = os.path.join("data", "settings", f"{setting_id}.json")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(setting_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def load_setting(setting_id):
    """設定をファイルから読み込む"""
    filepath = os.path.join("data", "settings", f"{setting_id}.json")
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        setting_data = json.load(f)
    
    return setting_data