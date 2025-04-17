import os
import json
import uuid
from api import grok_api
from services import story_service, setting_service, synopsis_service

def generate_multiple_endings(story_id, num_endings=3, ending_types=None):
    """
    既存の物語に対して複数のエンディングを生成する
    
    Args:
        story_id (str): 物語ID
        num_endings (int): 生成するエンディングの数
        ending_types (list, optional): エンディングのタイプのリスト
            例: ["happy", "tragic", "open", "twist", "bittersweet"]
            
    Returns:
        dict: 生成されたエンディングを含む辞書
    """
    # デフォルトのエンディングタイプ
    if not ending_types:
        ending_types = ["happy", "tragic", "open"]
    
    # 物語データを取得
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    # 物語のテキスト
    story_text = story_data.get("text", "")
    
    # シノプシスデータを取得
    synopsis_id = story_data.get("synopsis_id")
    synopsis_data = synopsis_service.load_synopsis(synopsis_id)
    
    # シノプシスがない場合は早期リターン
    if not synopsis_data:
        return {"error": "物語に関連するあらすじが見つかりません"}
    
    # シノプシスのインデックス
    synopsis_index = story_data.get("synopsis_index", 0)
    
    # 選択されたあらすじを取得
    synopses = synopsis_data.get("synopses", [])
    if not isinstance(synopses, list) or synopsis_index >= len(synopses):
        return {"error": "指定されたあらすじが存在しません"}
    
    selected_synopsis = synopses[synopsis_index]
    
    # スタイルを取得
    style = story_data.get("style", "murakami")
    
    # エンディングタイプの説明
    ending_type_descriptions = {
        "happy": "満足感のある、肯定的な結末。登場人物の欲望が満たされ、解決や和解がある。",
        "tragic": "悲劇的な結末。喪失、別れ、後悔、または破滅的な結果に至る。",
        "open": "開かれた結末。物語は完全に締めくくられず、読者に解釈の余地を残す。",
        "twist": "予想外の展開がある結末。読者の期待を裏切る意外な方向に物語が進む。",
        "bittersweet": "苦甘い結末。ポジティブとネガティブの両方の要素を含み、喜びと痛みが混在する。",
        "circular": "循環的な結末。物語が始まりに戻るか、同様のパターンが繰り返される暗示がある。",
        "reflective": "内省的な結末。主人公の内面の変化や気づきに焦点を当てる。",
        "ambiguous": "曖昧な結末。複数の解釈が可能で、意図的に明確な答えを避ける。"
    }
    
    # 生成するエンディング数を制限
    num_endings = min(num_endings, len(ending_types), 5)
    
    # 各エンディングタイプに対してAPIを呼び出し
    endings = []
    
    for i in range(num_endings):
        ending_type = ending_types[i] if i < len(ending_types) else "standard"
        ending_description = ending_type_descriptions.get(ending_type, "標準的な結末")
        
        prompt = f"""
        以下の官能小説に対して、「{ending_type}」タイプの結末を生成してください。
        
        物語の内容:
        {story_text}
        
        あらすじ情報:
        {json.dumps(selected_synopsis, ensure_ascii=False)}
        
        エンディングタイプ: {ending_type}
        説明: {ending_description}
        
        以下の条件に従って結末を生成してください:
        1. 物語の展開と登場人物に一貫性のある結末にする
        2. 既に書かれた部分との自然な接続を意識する
        3. 指定されたエンディングタイプの特性を持つようにする
        4. 文体は「{style}」スタイルを維持する
        5. 結末の長さは500-800文字程度に
        6. 数値的な体のサイズへの言及は避け、より文学的な表現を用いる
        7. 村上龍のようなハードボイルドな描写と、リアルな人間の欲望や葛藤を描く
        
        結末を生成してください。
        """
        
        # API呼び出し
        ending_text = grok_api.generate_text(prompt, max_tokens=2000)
        
        # 結果をフォーマット
        ending = {
            "ending_type": ending_type,
            "ending_description": ending_description,
            "ending_text": ending_text
        }
        
        endings.append(ending)
    
    # 複数のエンディングをまとめる
    result = {
        "story_id": story_id,
        "chapter": story_data.get("chapter", 1),
        "style": style,
        "endings": endings
    }
    
    # エンディングの保存
    ending_id = str(uuid.uuid4())
    save_endings(ending_id, result)
    
    # 結果にIDを追加
    result["id"] = ending_id
    
    return result

def save_endings(ending_id, ending_data):
    """エンディングをファイルに保存する"""
    filepath = os.path.join("data", "endings", f"{ending_id}.json")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(ending_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def load_endings(ending_id):
    """エンディングをファイルから読み込む"""
    filepath = os.path.join("data", "endings", f"{ending_id}.json")
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        ending_data = json.load(f)
    
    return ending_data

def integrate_ending(story_id, ending_id, selected_ending_index=0):
    """
    選択されたエンディングを物語に統合する
    
    Args:
        story_id (str): 物語ID
        ending_id (str): エンディングID
        selected_ending_index (int): 選択されたエンディングのインデックス
        
    Returns:
        dict: 統合された物語
    """
    # 物語データを取得
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    # エンディングデータを取得
    ending_data = load_endings(ending_id)
    if not ending_data:
        return {"error": "指定されたエンディングが見つかりません"}
    
    # エンディングのリスト
    endings = ending_data.get("endings", [])
    
    # インデックスが範囲内かチェック
    if not endings or selected_ending_index >= len(endings):
        return {"error": "指定されたエンディングインデックスが無効です"}
    
    # 選択されたエンディング
    selected_ending = endings[selected_ending_index]
    
    # 物語のテキスト
    story_text = story_data.get("text", "")
    
    # エンディングのテキスト
    ending_text = selected_ending.get("ending_text", "")
    
    # 物語とエンディングを統合するためのプロンプト
    prompt = f"""
    以下の官能小説と選択されたエンディングを自然に統合してください。
    
    物語の内容:
    {story_text}
    
    選択されたエンディング:
    {ending_text}
    
    以下の条件に従って統合してください:
    1. 物語からエンディングへの自然な接続を作る
    2. 重複や矛盾がないようにする
    3. 一貫した文体とトーンを維持する
    4. 必要に応じて小さな調整を行い、全体の流れをスムーズにする
    
    統合された完全な物語を返してください。
    """
    
    # API呼び出し
    integrated_text = grok_api.generate_text(prompt, max_tokens=len(story_text) + len(ending_text) + 500)
    
    # 結果をフォーマット
    integrated_story = dict(story_data)
    integrated_story["text"] = integrated_text
    integrated_story["integrated_ending"] = {
        "ending_id": ending_id,
        "ending_type": selected_ending.get("ending_type", "standard"),
        "ending_index": selected_ending_index
    }
    
    # 統合された物語の保存
    integrated_id = str(uuid.uuid4())
    story_service.save_story(integrated_id, integrated_story)
    
    return {
        "id": integrated_id,
        "chapter": integrated_story.get("chapter", 1),
        "text": integrated_text,
        "ending_type": selected_ending.get("ending_type", "standard")
    }