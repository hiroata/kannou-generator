import os
import json
import uuid
from api import grok_api
from services import setting_service
from config import WRITING_STYLES

def generate_synopses(setting_id, model="grok", style="murakami", num_synopses=1):
    """
    設定に基づいてあらすじを生成する
    
    Args:
        setting_id (str): 設定ID
        model (str): 使用するモデル ('grok' のみサポート)
        style (str): 文体スタイル ('murakami' または 'dan')
        num_synopses (int): 生成するあらすじの数
    
    Returns:
        dict: 生成されたあらすじを含む辞書
    """
    # 設定の読み込み
    setting_data = setting_service.load_setting(setting_id)
    if not setting_data:
        return {"error": "設定が見つかりません"}
    
    # モデルの強制
    model = "grok"  # 現在はgrokのみサポート
    
    # 文体の選択
    writing_style = WRITING_STYLES.get(style, WRITING_STYLES["murakami"])
    
    # プロンプトの作成
    prompt = f"""
    あなたは18禁官能小説のあらすじジェネレーターです。以下の設定に基づいて、{writing_style}で{num_synopses}つのあらすじを作成してください。
    
    設定:
    {json.dumps(setting_data, ensure_ascii=False)}
    
    各あらすじには以下を含めてください:
    - タイトル（官能的なニュアンスを含む魅力的なタイトル）
    - 導入部（物語がどのように始まるか、キャラクターの初期状況）
    - 展開（性的な緊張が高まる過程、露骨な性的表現を含む）
    - クライマックス（性的な頂点、最も卑猥で露骨な部分）
    - 結末（物語の結末と余韻）
    
    あらすじ全体を通して、以下の点に注意してください：
    - 性器や性行為を直接的に表現する言葉を積極的に使用する
    - 登場人物の性的な反応や感覚を詳細に描写する
    - 卑猥なセリフや淫語を含める
    - 性的な緊張と解放を明確に表現する
    
    以下の形式のJSONで回答してください:
    {{
      "stories": [
        {{
          "title": "タイトル1",
          "導入部": "導入部の内容...",
          "展開": "展開の内容...",
          "クライマックス": "クライマックスの内容...",
          "結末": "結末の内容..."
        }},
        ...
      ]
    }}
    
    必ず完全かつ構文的に有効なJSONを返してください。
    """
    
    # Grok APIを呼び出し
    response = grok_api.generate_text(prompt, max_tokens=4000)
    
    # レスポンスがAPIエラーメッセージを含むかチェック
    if response.startswith("エラーが発生しました"):
        return {"id": str(uuid.uuid4()), "synopses": {"error": "正しい形式で取得できませんでした", "raw_response": response}}
    
    # JSONパース処理
    try:
        # JSON部分の抽出（レスポンスが純粋なJSONでない場合に対応）
        json_str = extract_json(response)
        if not json_str:
            raise ValueError("レスポンスからJSONを抽出できません")
            
        # JSONパース
        parsed_data = json.loads(json_str)
        
        # "stories"キーがある場合はその内容を取得
        if isinstance(parsed_data, dict) and "stories" in parsed_data:
            synopses_data = parsed_data["stories"]
        else:
            # なければそのまま使用
            synopses_data = parsed_data
        
        # リストでない場合はリストに変換
        if not isinstance(synopses_data, list):
            synopses_data = [synopses_data]
        
        # 各あらすじの構造を確認・修正
        for i, synopsis in enumerate(synopses_data):
            if not isinstance(synopsis, dict):
                synopses_data[i] = {"title": "エラー", "導入部": "不正な形式", "展開": "", "クライマックス": "", "結末": ""}
                continue
                
            # 必須フィールドが存在するか確認
            for field in ["title", "導入部", "展開", "クライマックス", "結末"]:
                if field not in synopsis:
                    synopsis[field] = "情報なし"
                    
            # titleがメソッドの場合の対応
            if not isinstance(synopsis.get("title", ""), str) or callable(synopsis.get("title")):
                synopsis["title"] = "無題のあらすじ"
        
    except json.JSONDecodeError as e:
        print(f"JSON Parse error: {e}")
        print(f"Response content: {response[:1000]}")
        synopses_data = [{"title": "JSONパースエラー", "導入部": f"APIからの応答をJSONとして解析できませんでした: {str(e)}", "展開": "", "クライマックス": "", "結末": ""}]
    except Exception as e:
        print(f"Error processing API response: {e}")
        print(f"Response content: {response[:1000]}")
        synopses_data = [{"title": "処理エラー", "導入部": f"エラー: {str(e)}", "展開": "", "クライマックス": "", "結末": ""}]
    
    # あらすじの保存
    synopsis_id = str(uuid.uuid4())
    save_synopsis(synopsis_id, synopses_data, setting_id)
    
    return {"id": synopsis_id, "synopses": synopses_data}

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