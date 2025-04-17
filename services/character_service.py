import os
import json
import uuid
import random
from api import grok_api

# 詳細なキャラクターシート生成サービス
def generate_detailed_character_sheet(character_data, depth_level=3):
    """
    キャラクターの詳細なプロファイルを生成する
    
    Args:
        character_data (dict): 基本的なキャラクター情報
        depth_level (int): 詳細度レベル（1-5）
        
    Returns:
        dict: 詳細化されたキャラクターデータ
    """
    name = character_data.get("name", "名前不明")
    age = character_data.get("age", 25)
    basic_physical = character_data.get("physical_features", "")
    basic_personality = character_data.get("personality", "")
    
    prompt = f"""
    以下のキャラクター情報を、より精緻で深みのある官能小説のキャラクターシートに発展させてください。
    単純な体のサイズ（バストサイズなど）への言及は避け、代わりに文学的で描写的な表現を用いてください。
    村上龍のようなハードボイルドで精緻な描写を心がけてください。
    
    基本情報:
    名前: {name}
    年齢: {age}
    身体的特徴: {basic_physical}
    性格: {basic_personality}
    
    以下の要素を含む、詳細な文学的キャラクター描写を作成してください:
    
    1. 外見の詳細描写 - 体型、動き方、特徴的な仕草、視線、表情などを含む（数値的な表現は避け、比喩や感覚的な描写を重視）
    2. 心理的プロファイル - 内面の葛藤、トラウマ、欲望の源泉、価値観、恐れ、理性と欲望の間での葛藤など
    3. 性的嗜好と欲望 - 性的な好み、ファンタジー、抑圧された欲求、性的経験の歴史、性的自己認識など
    4. 社会的関係性 - 他者との関わり方、権力関係への態度、親密さへの姿勢、信頼と裏切りに関する過去の経験など
    5. 過去の形成的経験 - 性格形成に影響を与えた重要な出来事、関係性、決断など
    
    すべての要素は相互に関連し、一貫性のある複雑な人物像を形成するようにしてください。
    露骨さレベル: {depth_level}（1は控えめ、5は非常に露骨）に応じて表現を調整してください。
    
    出力は以下のJSON形式で返してください:
    {{
      "name": "{name}",
      "age": {age},
      "physical_detail": "詳細な身体描写（数値的表現を避け、文学的表現を使用）",
      "psychological_profile": "詳細な心理プロファイル",
      "sexual_preferences": "性的嗜好の詳細",
      "social_dynamics": "対人関係の動態",
      "formative_experiences": "形成的経験",
      "voice_pattern": "会話や内的独白の特徴的なパターン",
      "inner_conflicts": "内的葛藤",
      "outward_facade": "外面的な仮面と内面の対比"
    }}
    """
    
    # API呼び出し
    response = grok_api.generate_text(prompt, max_tokens=2500)
    
    # JSONパースとエラー処理
    try:
        # JSON部分の抽出
        json_str = extract_json(response)
        if json_str:
            character_detail = json.loads(json_str)
        else:
            character_detail = {"error": "詳細情報の生成に失敗しました"}
    except Exception as e:
        print(f"キャラクター詳細のパース中にエラー: {e}")
        character_detail = {"error": f"データ処理エラー: {str(e)}"}
    
    return character_detail

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

def generate_character_relationships(characters, relationship_type="complex"):
    """
    キャラクター間の複雑な関係性を生成する
    
    Args:
        characters (list): キャラクターのリスト
        relationship_type (str): 関係性のタイプ（"complex", "hierarchical", "conflicted"など）
        
    Returns:
        dict: キャラクター間の関係性のマップ
    """
    if len(characters) < 2:
        return {"error": "関係性の生成には少なくとも2人のキャラクターが必要です"}
    
    # キャラクター名のリスト作成
    character_names = [char.get("name", f"キャラクター{i+1}") for i, char in enumerate(characters)]
    
    prompt = f"""
    以下のキャラクター間の複雑な関係性マップを作成してください。村上龍のようなハードボイルドな人間関係と、背景に潜む暗い欲望や権力関係を表現してください。

    キャラクター:
    {', '.join(character_names)}
    
    関係性タイプ: {relationship_type}
    
    以下の要素を含む関係性マップを生成してください:
    1. 表面的な関係性 - 社会的に見える関係（同僚、友人、恋人、家族など）
    2. 隠された関係性 - 表面下にある真の関係（欲望、嫉妬、支配、依存など）
    3. 権力のダイナミクス - 誰が誰に対して力を持っているか、その力の源泉は何か
    4. 性的緊張関係 - 性的な魅力、欲望、葛藤、履歴
    5. 過去の関連性 - 共有される過去の出来事、記憶、トラウマ
    
    キャラクターごとに、他のすべてのキャラクターとの関係を詳細に記述してください。
    
    出力は以下のJSON形式で返してください:
    {{
      "relationships": [
        {{
          "from": "キャラクター1の名前",
          "to": "キャラクター2の名前",
          "surface_relationship": "表面的な関係の説明",
          "hidden_dynamic": "隠された関係性の説明",
          "power_dynamic": "権力関係の説明",
          "sexual_tension": "性的緊張の説明",
          "shared_history": "共有する過去の説明"
        }},
        // 他のすべてのキャラクターペアに対して同様に
      ]
    }}
    """
    
    # API呼び出し
    response = grok_api.generate_text(prompt, max_tokens=3000)
    
    # JSONパースとエラー処理
    try:
        json_str = extract_json(response)
        if json_str:
            relationships = json.loads(json_str)
        else:
            relationships = {"error": "関係性マップの生成に失敗しました"}
    except Exception as e:
        print(f"関係性マップのパース中にエラー: {e}")
        relationships = {"error": f"データ処理エラー: {str(e)}"}
    
    return relationships

def save_detailed_character(character_id, character_data):
    """詳細なキャラクターをファイルに保存する"""
    filepath = os.path.join("data", "characters", f"{character_id}.json")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(character_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def load_detailed_character(character_id):
    """詳細なキャラクターをファイルから読み込む"""
    filepath = os.path.join("data", "characters", f"{character_id}.json")
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        character_data = json.load(f)
    
    return character_data

def generate_character_voice_sample(character_data, scenario="intimate"):
    """
    キャラクターの声や話し方のサンプルを生成する
    
    Args:
        character_data (dict): キャラクターデータ
        scenario (str): シナリオタイプ（"intimate", "public", "internal"など）
        
    Returns:
        dict: キャラクターの会話サンプル
    """
    name = character_data.get("name", "名前不明")
    psychological_profile = character_data.get("psychological_profile", "")
    voice_pattern = character_data.get("voice_pattern", "")
    
    scenarios = {
        "intimate": "親密な状況での会話と内的独白",
        "public": "公の場での会話と内的独白",
        "emotional": "感情的な状況での会話と内的独白",
        "sexual": "性的興奮時の会話と内的独白",
        "conflicted": "内的葛藤を抱えた状況での会話と内的独白"
    }
    
    scenario_desc = scenarios.get(scenario, scenarios["intimate"])
    
    prompt = f"""
    以下のキャラクターの会話パターンと内的独白のサンプルを生成してください。
    村上龍のようなハードボイルドで真実味のある表現を使用してください。

    キャラクター名: {name}
    心理プロファイル: {psychological_profile}
    声のパターン: {voice_pattern}
    
    シナリオ: {scenario_desc}
    
    以下の要素を含むサンプルを生成してください:
    1. 通常の会話（3-5のセリフ例）
    2. 内的独白（3-5の例）
    3. 感情的/刺激的状況下での言葉（3-5の例）
    4. 特徴的な言い回しや口癖（2-3の例）
    
    出力は以下のJSON形式で返してください:
    {{
      "character_name": "{name}",
      "dialogue_samples": [
        "セリフ例1",
        "セリフ例2",
        ...
      ],
      "inner_monologue_samples": [
        "内的独白例1",
        "内的独白例2",
        ...
      ],
      "emotional_expressions": [
        "感情表現例1",
        "感情表現例2",
        ...
      ],
      "catchphrases": [
        "特徴的な表現1",
        "特徴的な表現2",
        ...
      ],
      "voice_characteristics": "声や話し方の特徴の総合的な説明"
    }}
    """
    
    # API呼び出し
    response = grok_api.generate_text(prompt, max_tokens=2000)
    
    # JSONパースとエラー処理
    try:
        json_str = extract_json(response)
        if json_str:
            voice_samples = json.loads(json_str)
        else:
            voice_samples = {"error": "会話サンプルの生成に失敗しました"}
    except Exception as e:
        print(f"会話サンプルのパース中にエラー: {e}")
        voice_samples = {"error": f"データ処理エラー: {str(e)}"}
    
    return voice_samples