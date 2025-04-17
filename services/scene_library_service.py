import os
import json
import uuid
import random
from api import grok_api

# シーンタイプのカテゴリ
SCENE_CATEGORIES = {
    "first_encounter": "初めての出会い/関係",
    "office": "オフィスでの密会",
    "travel": "旅行中のシーン",
    "public": "公共の場でのシーン",
    "domestic": "家庭内のシーン",
    "fantasy": "空想/夢/妄想",
    "power_dynamic": "権力関係",
    "emotional": "感情的な葛藤",
    "reconciliation": "和解/許し",
    "betrayal": "裏切り/発覚",
    "forbidden": "禁断の関係",
}

def get_scene_categories():
    """利用可能なシーンカテゴリを取得する"""
    return SCENE_CATEGORIES

def generate_scene_template(category, explicitness_level=3, style="murakami"):
    """
    特定のカテゴリのシーンテンプレートを生成する
    
    Args:
        category (str): シーンカテゴリ
        explicitness_level (int): 露骨さのレベル（1-5）
        style (str): 文体スタイル（"murakami"または"dan"）
        
    Returns:
        dict: 生成されたシーンテンプレート
    """
    category_desc = SCENE_CATEGORIES.get(category, "一般的なシーン")
    
    # 文体の選択
    style_desc = ""
    if style == "murakami":
        style_desc = """
        村上龍のようなハードボイルドで都会的な文体。
        - 冷静で観察的な描写
        - 性描写は生々しく直接的だが、感情的な装飾は少なめ
        - 社会的な疎外感や虚無感を背景に
        - 都市の孤独や人間関係の空虚さを描写
        - 性行為の物理的側面と内面の乖離を強調
        - 短めの文とリズミカルな文体
        """
    elif style == "dan":
        style_desc = """
        団鬼六のようなSM描写に特化した文体。
        - 支配と服従の関係性に焦点
        - 拘束や調教の詳細な描写
        - 痛みと快楽の混合
        - 儀式的、様式的な表現
        - 精神的な支配関係の描写
        - 羞恥心を強調した表現
        """
    else:
        style_desc = "標準的な官能小説の文体"
    
    prompt = f"""
    以下のカテゴリと条件に基づいた官能小説のシーンテンプレートを生成してください。
    サイズや年齢への定型的な言及は避け、より文学的で深みのある性描写を心がけてください。

    カテゴリ: {category_desc}
    露骨さレベル: {explicitness_level}（1は控えめ、5は非常に露骨）
    文体スタイル: {style_desc}
    
    以下の要素を含むテンプレートを作成してください:
    1. シーンの基本設定 - 場所、時間、雰囲気、環境の描写
    2. 登場人物の基本的な状態 - 心理状態、服装、姿勢、関係性など
    3. シーンの展開パターン - 導入から展開、クライマックスまでの流れ
    4. 特徴的な官能表現 - このタイプのシーンに適した比喩、言い回し、表現技法
    5. 感覚的描写のポイント - 視覚、聴覚、触覚、嗅覚、味覚の各要素でのポイント
    
    テンプレートは新しいキャラクターや状況に適用できる汎用的なものにしてください。
    具体的なキャラクター名や固有名詞は「[名前1]」「[名前2]」のようなプレースホルダーを使用してください。
    
    出力は以下のJSON形式で返してください:
    {{
      "category": "{category}",
      "explicitness_level": {explicitness_level},
      "style": "{style}",
      "title": "シーンのタイトル",
      "setting": "シーンの基本設定（場所、時間など）",
      "character_states": "登場人物の状態（心理、外見など）",
      "progression_pattern": "シーンの展開パターン",
      "sensory_highlights": {{
        "visual": "視覚的描写のポイント",
        "auditory": "聴覚的描写のポイント",
        "tactile": "触覚的描写のポイント",
        "olfactory": "嗅覚的描写のポイント",
        "gustatory": "味覚的描写のポイント"
      }},
      "key_expressions": [
        "特徴的な表現1",
        "特徴的な表現2",
        "特徴的な表現3"
      ],
      "template_text": "完全なテンプレートテキスト（400-600文字程度）"
    }}
    """
    
    # API呼び出し
    response = grok_api.generate_text(prompt, max_tokens=3000)
    
    # JSONパースとエラー処理
    try:
        # JSON部分の抽出
        json_str = extract_json(response)
        if json_str:
            scene_template = json.loads(json_str)
        else:
            scene_template = {"error": "シーンテンプレートの生成に失敗しました"}
    except Exception as e:
        print(f"シーンテンプレートのパース中にエラー: {e}")
        scene_template = {"error": f"データ処理エラー: {str(e)}"}
    
    return scene_template

def extract_json(text):
    """テキストからJSON部分を抽出する"""
    start = text.find('{')
    if start == -1:
        return None
        
    brackets = 0
    in_string = False
    escaped = False
    
    for i in range(start, len(text)):
        char = text[i]
        
        if char == '\\' and not escaped:
            escaped = True
            continue
            
        if char == '"' and not escaped:
            in_string = not in_string
            
        if not in_string:
            if char == '{':
                brackets += 1
            elif char == '}':
                brackets -= 1
                if brackets == 0:
                    return text[start:i+1]
        
        escaped = False if char != '\\' or escaped else True
    
    return None

def save_scene_template(template_id, template_data):
    """シーンテンプレートをファイルに保存する"""
    filepath = os.path.join("data", "scene_templates", f"{template_id}.json")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(template_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def load_scene_template(template_id):
    """シーンテンプレートをファイルから読み込む"""
    filepath = os.path.join("data", "scene_templates", f"{template_id}.json")
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        template_data = json.load(f)
    
    return template_data

def list_scene_templates():
    """保存されているすべてのシーンテンプレートをリストアップする"""
    template_dir = os.path.join("data", "scene_templates")
    os.makedirs(template_dir, exist_ok=True)
    
    templates = []
    for filename in os.listdir(template_dir):
        if filename.endswith(".json"):
            template_id = filename[:-5]  # .jsonを除去
            template_data = load_scene_template(template_id)
            if template_data and "error" not in template_data:
                templates.append({
                    "id": template_id,
                    "title": template_data.get("title", "無題"),
                    "category": template_data.get("category", "一般"),
                    "explicitness_level": template_data.get("explicitness_level", 3),
                    "style": template_data.get("style", "standard")
                })
    
    return templates

def apply_scene_template(template_id, characters, custom_setting=None):
    """
    シーンテンプレートを特定のキャラクターに適用する
    
    Args:
        template_id (str): テンプレートID
        characters (list): キャラクターデータのリスト
        custom_setting (str, optional): カスタム設定（指定がなければテンプレートの設定を使用）
        
    Returns:
        dict: 適用されたシーン
    """
    # テンプレート読み込み
    template = load_scene_template(template_id)
    if not template or "error" in template:
        return {"error": "テンプレートの読み込みに失敗しました"}
    
    # キャラクター情報の抽出
    character_info = []
    for i, char in enumerate(characters):
        character_info.append({
            "placeholder": f"[名前{i+1}]",
            "name": char.get("name", f"キャラクター{i+1}"),
            "physical": char.get("physical_detail", char.get("physical_features", "")),
            "personality": char.get("psychological_profile", char.get("personality", ""))
        })
    
    # 設定の選択
    setting = custom_setting if custom_setting else template.get("setting", "")
    
    prompt = f"""
    以下のシーンテンプレートを、指定されたキャラクターに適用して具体的なシーンを生成してください。
    
    テンプレート情報:
    タイトル: {template.get("title", "無題")}
    カテゴリ: {template.get("category", "一般")}
    基本設定: {setting}
    展開パターン: {template.get("progression_pattern", "")}
    
    キャラクター情報:
    {json.dumps(character_info, ensure_ascii=False, indent=2)}
    
    テンプレートテキスト:
    {template.get("template_text", "")}
    
    以下の指示に従ってテンプレートを具体的なシーンに変換してください:
    1. テンプレートのプレースホルダー（[名前1]など）を実際のキャラクター名に置き換える
    2. キャラクターの特性に合わせて描写を調整する
    3. 感覚的な描写（{template.get("sensory_highlights", {})})を活かす
    4. 提供された特徴的表現（{template.get("key_expressions", [])})を適切に組み込む
    5. 文体と露骨さのレベルを維持する
    
    シーンは800-1200文字程度で生成してください。
    """
    
    # API呼び出し
    applied_scene_text = grok_api.generate_text(prompt, max_tokens=4000)
    
    # 結果をフォーマット
    applied_scene = {
        "template_id": template_id,
        "template_title": template.get("title", "無題"),
        "template_category": template.get("category", "一般"),
        "characters": [char.get("name", f"キャラクター{i+1}") for i, char in enumerate(characters)],
        "setting": setting,
        "scene_text": applied_scene_text
    }
    
    return applied_scene

def generate_scene_variation(scene_text, variation_type="intensity", direction="increase"):
    """
    既存のシーンのバリエーションを生成する
    
    Args:
        scene_text (str): 元のシーンテキスト
        variation_type (str): バリエーションのタイプ
            - "intensity": 強度/露骨さ
            - "emotion": 感情的要素
            - "detail": 詳細度
            - "pacing": テンポ/ペース
            - "pov": 視点の変更
        direction (str): 変化の方向
            - "increase": 増加/強化
            - "decrease": 減少/抑制
            - "shift": 視点や焦点のシフト
            
    Returns:
        dict: 生成されたバリエーション
    """
    variation_descriptions = {
        "intensity": {
            "increase": "より露骨で直接的な表現に",
            "decrease": "より控えめで暗示的な表現に"
        },
        "emotion": {
            "increase": "感情的要素と心理描写を強化",
            "decrease": "感情表現を抑え、物理的描写に集中"
        },
        "detail": {
            "increase": "より詳細な描写と感覚表現を追加",
            "decrease": "余計な詳細を省き、簡潔な表現に"
        },
        "pacing": {
            "increase": "テンポを上げ、緊張感を高める",
            "decrease": "テンポを落とし、じっくりと描写"
        },
        "pov": {
            "shift": "視点を変更（一人称/三人称、または登場人物間）"
        }
    }
    
    variation_desc = variation_descriptions.get(variation_type, {}).get(direction, "標準的な変更")
    
    prompt = f"""
    以下の官能シーンを、指定された方向に変化させたバリエーションを生成してください。
    
    元のシーン:
    {scene_text}
    
    変更タイプ: {variation_type}
    変更方向: {direction}
    詳細: {variation_desc}
    
    変更にあたっての指示:
    1. 元のシーンの基本的な状況と登場人物は維持する
    2. 指定された変更を加えて、新しいニュアンスや表現を導入する
    3. 文章量は元のテキストとほぼ同じにする
    4. 村上龍風のハードボイルドで都会的な文体を維持する
    5. 数値的な身体描写ではなく、文学的な表現を用いる
    
    バリエーションシーンを生成してください。
    """
    
    # API呼び出し
    variation_text = grok_api.generate_text(prompt, max_tokens=len(scene_text) * 1.5)
    
    # 結果をフォーマット
    variation = {
        "original_length": len(scene_text),
        "variation_length": len(variation_text),
        "variation_type": variation_type,
        "variation_direction": direction,
        "variation_description": variation_desc,
        "variation_text": variation_text
    }
    
    return variation