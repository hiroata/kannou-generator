import os
import json
import uuid
import re
import random
import importlib
from api import grok_api
from config import WRITING_STYLES, AVAILABLE_MODELS

# 日本人名リスト（一部）
JAPANESE_MALE_NAMES = [
    "悠太", "遼", "健太", "大輔", "拓也", "翔太", "雄大", "健太郎", "大輔", "修平",
    "直樹", "健太", "洋平", "和也", "貴大", "和樹", "智樹", "翔太", "大介", "雄太",
    "拓也", "拓也", "拓真", "慎太郎", "健", "大輔", "直樹", "健太", "智也"
]

JAPANESE_FEMALE_NAMES = [
    "さくら", "美咲", "陽子", "美香", "裕子", "千尋", "恵", "美紀", "由佳", "麻衣",
    "理沙", "直美", "香織", "純子", "愛", "明美", "七海", "美穂", "裕美", "麻衣子",
    "由佳", "裕子", "恵美", "真由美", "彩", "麻美", "直子", "美香", "由美子"
]

JAPANESE_SURNAMES = [
    "佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村", "小林", "加藤",
    "吉田", "山田", "佐々木", "山口", "松本", "井上", "木村", "林", "斎藤", "清水",
    "山崎", "中島", "池田", "阿部", "橋本", "山下", "森", "松田", "小川", "中島"
]

def generate_random_name(gender=None):
    """ランダムな日本人名を生成する"""
    if gender == "male" or (gender is None and random.random() < 0.5):
        first_name = random.choice(JAPANESE_MALE_NAMES)
        gender = "male"
    else:
        first_name = random.choice(JAPANESE_FEMALE_NAMES)
        gender = "female"
        
    last_name = random.choice(JAPANESE_SURNAMES)
    
    return {
        "first_name": first_name,
        "last_name": last_name,
        "full_name": f"{last_name}{first_name}",
        "gender": gender
    }

def replace_names_in_text(text, name_mapping):
    """テキスト内の名前を置き換える"""
    result = text
    for old_name, new_name in name_mapping.items():
        # 名前の置換（フルネームと姓名それぞれ）
        if len(old_name.split()) > 1:  # 姓名が分かれている場合
            old_parts = old_name.split()
            # フルネーム（スペース区切り）の置換
            result = re.sub(r'\b' + re.escape(old_name) + r'\b', 
                           new_name["full_name"], 
                           result, 
                           flags=re.IGNORECASE)
            # 姓のみの置換
            result = re.sub(r'\b' + re.escape(old_parts[0]) + r'\b', 
                           new_name["last_name"], 
                           result, 
                           flags=re.IGNORECASE)
            # 名のみの置換
            if len(old_parts) > 1:
                result = re.sub(r'\b' + re.escape(old_parts[1]) + r'\b', 
                               new_name["first_name"], 
                               result, 
                               flags=re.IGNORECASE)
        else:  # 単一の名前の場合
            result = re.sub(r'\b' + re.escape(old_name) + r'\b', 
                           new_name["full_name"], 
                           result, 
                           flags=re.IGNORECASE)
    
    return result

def extract_names_from_text(text):
    """テキストから人名らしき単語を抽出する（簡易版）"""
    # 日本人の名前っぽいパターン（苗字+名前、「さん」「君」などの敬称付き）
    name_patterns = [
        r'([一-龠々]+)([一-龠あ-んア-ン]+)',  # 漢字+漢字またはかな（フルネーム）
        r'([一-龠々]+)さん',  # 漢字+さん
        r'([一-龠あ-んア-ン]+)くん',  # 名前+くん
        r'([一-龠あ-んア-ン]+)ちゃん',  # 名前+ちゃん
        r'([一-龠あ-んア-ン]+)さん',  # 名前+さん
    ]
    
    potential_names = []
    for pattern in name_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                for part in match:
                    if len(part) > 1:  # 一文字の名前は除外
                        potential_names.append(part)
            elif len(match) > 1:  # 一文字の名前は除外
                potential_names.append(match)
    
    # 重複を排除して返す
    return list(set(potential_names))

def generate_setting_from_scenario(model="grok", scenario=""):
    """シナリオテキストから設定を生成する"""
    # モデル指定がない場合はgrokをデフォルトに
    if not model in AVAILABLE_MODELS:
        model = "grok"
        
    # APIモジュールの動的インポート
    api_module_name = AVAILABLE_MODELS[model]["api_module"]
    try:
        api_module = importlib.import_module(f"api.{api_module_name}")
    except ImportError:
        return {"error": f"APIモジュール {api_module_name} のインポートに失敗しました"}
    
    # シナリオからキャラクター名を抽出し、ランダムな名前に変換
    extracted_names = extract_names_from_text(scenario)
    name_mapping = {}
    
    for name in extracted_names:
        # 長すぎる名前や短すぎる名前は除外
        if 1 < len(name) < 6:
            # 簡易的な性別判定（実際はもっと複雑な処理が必要）
            gender = "female" if any(char in "子美香恵佳菜絵" for char in name) else "male"
            name_mapping[name] = generate_random_name(gender)
    
    # シナリオ内の名前を置換
    modified_scenario = replace_names_in_text(scenario, name_mapping)
    
    # 設定生成のプロンプト
    prompt = f"""
    あなたは18禁官能小説の設定ジェネレーターです。以下のシナリオを元に、詳細で卑猥な設定を作成してください。
    エロティックな表現をより官能的に、より直接的に、そして登場人物の欲望を赤裸々に表現してください。
    
    ユーザーのシナリオ:
    {modified_scenario}
    
    以下の内容を含む詳細な設定を作成してください:
    1. 登場人物（名前、年齢、身体的特徴と詳細なサイズ感、性格、性的な嗜好や経験）
    2. 舞台設定（場所、時代）
    3. 背景状況（人間関係の詳細、性的関係、過去の経験など）
    
    卑猥な言葉や性的な描写をより生々しく、露骨に含めてください。以下の形式で出力してください:
    
    {{
      "type": "カスタム",
      "characters": [
        {{
          "name": "キャラクター1の名前",
          "age": 年齢（数字のみ）,
          "physical_features": "身体的特徴（バスト、ウエスト、ヒップなどの具体的なサイズや特徴）",
          "personality": "性格や性的嗜好の詳細"
        }},
        {{
          "name": "キャラクター2の名前",
          "age": 年齢（数字のみ）,
          "physical_features": "身体的特徴の詳細",
          "personality": "性格や性的嗜好の詳細"
        }},
        ...必要に応じて追加
      ],
      "setting": {{
        "location": "詳細な場所の説明",
        "era": "時代設定"
      }},
      "background": {{
        "relationship": "人間関係の詳細（性的な関係性も含む）"
      }}
    }}
    
    必ず完全かつ構文的に有効なJSONを返してください。性的表現は直接的かつ露骨に表現してください。
    """
    
    # API呼び出し
    response = api_module.generate_text(prompt, max_tokens=4000)
    
    # レスポンスがAPIエラーメッセージを含むかチェック
    if response.startswith("エラーが発生"):
        setting_data = {"error": "正しい形式で取得できませんでした", "raw_response": response}
    else:
        # JSON部分の抽出（レスポンスが純粋なJSONでない場合に対応）
        json_str = extract_json(response)
        
        # JSONパース（エラー処理）
        try:
            if json_str:
                setting_data = json.loads(json_str)
            else:
                # JSON抽出失敗
                setting_data = {"error": "JSON形式で取得できませんでした", "raw_response": response}
        except json.JSONDecodeError as e:
            print(f"JSON Parse error: {e}")
            setting_data = {"error": "正しい形式で取得できませんでした", "raw_response": response}
        except Exception as e:
            print(f"Error processing API response: {e}")
            setting_data = {"error": "正しい形式で取得できませんでした", "raw_response": str(e)}
    
    # 設定の保存
    setting_id = str(uuid.uuid4())
    save_setting(setting_id, setting_data)
    
    return {"id": setting_id, "setting": setting_data}

def generate_setting(model="grok", setting_type="一般", additional_details=""):
    """
    小説の設定を生成する
    
    Args:
        model (str): 使用するモデル ('grok', 'gemini')
        setting_type (str): 設定のタイプ
        additional_details (str): 追加の詳細
    
    Returns:
        dict: 生成された設定
    """
    # モデル指定がない場合はgrokをデフォルトに
    if not model in AVAILABLE_MODELS:
        model = "grok"
        
    # APIモジュールの動的インポート
    api_module_name = AVAILABLE_MODELS[model]["api_module"]
    try:
        api_module = importlib.import_module(f"api.{api_module_name}")
    except ImportError:
        return {"error": f"APIモジュール {api_module_name} のインポートに失敗しました"}
    
    prompt = f"""
    あなたは官能小説の設定ジェネレーターです。以下の条件で魅力的で淫らな設定を作成してください。

    タイプ: {setting_type}
    追加情報: {additional_details}
    
    以下の内容を含めてください:
    - 登場人物（名前、年齢、身体的特徴と詳細なサイズ、性格、性的な好み）を3-5人
    - 舞台設定（場所、時代）の詳細な説明
    - 背景状況（どのような関係性にあるか、性的な緊張関係など）
    
    登場人物の性的な特徴や関係性について露骨かつ詳細に記述してください。卑猥な言葉や性描写を積極的に取り入れてください。

    以下の形式の正確なJSONで回答してください:
    {{
      "type": "{setting_type}",
      "characters": [
        {{
          "name": "名前1",
          "age": 年齢,
          "physical_features": "身体的特徴（具体的な数値を含む）",
          "personality": "性格と性的嗜好"
        }},
        ...
      ],
      "setting": {{
        "location": "場所",
        "era": "時代"
      }},
      "background": {{
        "relationship": "人間関係の詳細（性的関係性を含む）..."
      }}
    }}
    
    必ず完全かつ構文的に有効なJSONを返してください。
    """
    
    # API呼び出し
    response = api_module.generate_text(prompt, max_tokens=3000)
    
    # レスポンスがAPIエラーメッセージを含むかチェック
    if response.startswith("エラーが発生しました"):
        setting_data = {"error": "正しい形式で取得できませんでした", "raw_response": response}
    else:
        # JSON部分の抽出（レスポンスが純粋なJSONでない場合に対応）
        json_str = extract_json(response)
        
        # JSONパース（エラー処理）
        try:
            if json_str:
                setting_data = json.loads(json_str)
            else:
                # JSON抽出失敗
                setting_data = {"error": "JSON形式で取得できませんでした", "raw_response": response}
        except json.JSONDecodeError as e:
            print(f"JSON Parse error: {e}")
            setting_data = {"error": "正しい形式で取得できませんでした", "raw_response": response}
        except Exception as e:
            print(f"Error processing API response: {e}")
            setting_data = {"error": "正しい形式で取得できませんでした", "raw_response": str(e)}
    
    # 設定の保存
    setting_id = str(uuid.uuid4())
    save_setting(setting_id, setting_data)
    
    return {"id": setting_id, "setting": setting_data}

def extract_json(text):
    """
    テキストからJSON部分を抽出する
    
    Args:
        text (str): 抽出元テキスト
    
    Returns:
        str: 抽出されたJSON文字列
    """
    # { から始まる部分を探す
    start = text.find('{')
    if start == -1:
        return None
        
    # 括弧の数をカウントしてJSONの終わりを特定
    brackets = 0
    in_string = False
    escaped = False
    
    for i in range(start, len(text)):
        char = text[i]
        
        # 文字列内のエスケープ処理
        if char == '\\' and not escaped:
            escaped = True
            continue
            
        # 文字列の開始/終了
        if char == '"' and not escaped:
            in_string = not in_string
            
        # 括弧のカウント（文字列内でない場合のみ）
        if not in_string:
            if char == '{':
                brackets += 1
            elif char == '}':
                brackets -= 1
                # 最初の開き括弧に対応する閉じ括弧を見つけた
                if brackets == 0:
                    return text[start:i+1]
        
        # エスケープフラグのリセット
        escaped = False if char != '\\' or escaped else True
    
    # 完全なJSONが見つからなかった場合
    return None

def save_setting(setting_id, setting_data):
    """設定をファイルに保存する"""
    filepath = os.path.join("data", "settings", f"{setting_id}.json")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
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