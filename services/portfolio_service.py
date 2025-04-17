import os
import json
import uuid
import shutil
from datetime import datetime
from services import story_service, setting_service, synopsis_service

def create_portfolio(title, description=""):
    """
    小説ポートフォリオを作成する
    
    Args:
        title (str): ポートフォリオのタイトル
        description (str): ポートフォリオの説明
        
    Returns:
        dict: 作成されたポートフォリオの情報
    """
    portfolio_id = str(uuid.uuid4())
    
    portfolio_data = {
        "id": portfolio_id,
        "title": title,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "stories": [],
        "settings": [],
        "characters": []
    }
    
    # ポートフォリオを保存
    save_portfolio(portfolio_id, portfolio_data)
    
    return portfolio_data

def add_story_to_portfolio(portfolio_id, story_id, title=None):
    """
    ポートフォリオに物語を追加する
    
    Args:
        portfolio_id (str): ポートフォリオID
        story_id (str): 物語ID
        title (str, optional): 物語のカスタムタイトル
        
    Returns:
        dict: 更新されたポートフォリオの情報
    """
    # ポートフォリオデータを取得
    portfolio_data = load_portfolio(portfolio_id)
    if not portfolio_data:
        return {"error": "指定されたポートフォリオが見つかりません"}
    
    # 物語データを取得
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    # すでに同じ物語がポートフォリオに含まれているかチェック
    for existing_story in portfolio_data.get("stories", []):
        if existing_story.get("id") == story_id:
            return {"error": "この物語はすでにポートフォリオに含まれています"}
    
    # 物語のタイトル（指定がなければ自動生成）
    story_title = title
    if not story_title:
        synopsis_id = story_data.get("synopsis_id")
        synopsis_index = story_data.get("synopsis_index", 0)
        chapter = story_data.get("chapter", 1)
        
        if synopsis_id:
            synopsis_data = synopsis_service.load_synopsis(synopsis_id)
            if synopsis_data and "synopses" in synopsis_data and isinstance(synopsis_data["synopses"], list):
                synopses = synopsis_data["synopses"]
                if 0 <= synopsis_index < len(synopses) and "title" in synopses[synopsis_index]:
                    story_title = f"{synopses[synopsis_index]['title']} - 第{chapter}章"
        
        if not story_title:
            story_title = f"無題の物語 #{len(portfolio_data.get('stories', [])) + 1}"
    
    # 物語をポートフォリオに追加
    story_info = {
        "id": story_id,
        "title": story_title,
        "added_at": datetime.now().isoformat(),
        "chapter": story_data.get("chapter", 1),
        "style": story_data.get("style", "murakami"),
        "setting_id": story_data.get("setting_id"),
        "synopsis_id": story_data.get("synopsis_id"),
        "synopsis_index": story_data.get("synopsis_index", 0)
    }
    
    portfolio_data["stories"].append(story_info)
    portfolio_data["updated_at"] = datetime.now().isoformat()
    
    # ポートフォリオを保存
    save_portfolio(portfolio_id, portfolio_data)
    
    return portfolio_data

def add_setting_to_portfolio(portfolio_id, setting_id, title=None):
    """
    ポートフォリオに設定を追加する
    
    Args:
        portfolio_id (str): ポートフォリオID
        setting_id (str): 設定ID
        title (str, optional): 設定のカスタムタイトル
        
    Returns:
        dict: 更新されたポートフォリオの情報
    """
    # ポートフォリオデータを取得
    portfolio_data = load_portfolio(portfolio_id)
    if not portfolio_data:
        return {"error": "指定されたポートフォリオが見つかりません"}
    
    # 設定データを取得
    setting_data = setting_service.load_setting(setting_id)
    if not setting_data:
        return {"error": "指定された設定が見つかりません"}
    
    # すでに同じ設定がポートフォリオに含まれているかチェック
    for existing_setting in portfolio_data.get("settings", []):
        if existing_setting.get("id") == setting_id:
            return {"error": "この設定はすでにポートフォリオに含まれています"}
    
    # 設定のタイトル（指定がなければ自動生成）
    setting_title = title
    if not setting_title:
        setting_type = setting_data.get("type", "一般")
        setting_location = setting_data.get("setting", {}).get("location", "不明な場所")
        setting_title = f"{setting_type}の設定 - {setting_location}"
    
    # 設定をポートフォリオに追加
    setting_info = {
        "id": setting_id,
        "title": setting_title,
        "added_at": datetime.now().isoformat(),
        "type": setting_data.get("type", "一般")
    }
    
    portfolio_data["settings"].append(setting_info)
    portfolio_data["updated_at"] = datetime.now().isoformat()
    
    # ポートフォリオを保存
    save_portfolio(portfolio_id, portfolio_data)
    
    return portfolio_data

def add_character_to_portfolio(portfolio_id, character_id, source_setting_id=None, title=None):
    """
    ポートフォリオにキャラクターを追加する
    
    Args:
        portfolio_id (str): ポートフォリオID
        character_id (str): キャラクターID（詳細キャラクターの場合）
        source_setting_id (str, optional): キャラクターの元となる設定ID
        title (str, optional): キャラクターのカスタムタイトル
        
    Returns:
        dict: 更新されたポートフォリオの情報
    """
    # ポートフォリオデータを取得
    portfolio_data = load_portfolio(portfolio_id)
    if not portfolio_data:
        return {"error": "指定されたポートフォリオが見つかりません"}
    
    # キャラクターデータを取得または生成
    character_data = None
    if character_id:
        character_data_path = os.path.join("data", "characters", f"{character_id}.json")
        if os.path.exists(character_data_path):
            with open(character_data_path, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
    
    if not character_data and source_setting_id:
        # 設定からキャラクターを抽出
        setting_data = setting_service.load_setting(source_setting_id)
        if not setting_data or "characters" not in setting_data:
            return {"error": "指定された設定からキャラクターを抽出できません"}
            
        # 設定内の全キャラクターをポートフォリオに追加
        for char in setting_data["characters"]:
            # すでに同じ名前のキャラクターがポートフォリオに含まれているかチェック
            char_name = char.get("name", "名前不明")
            duplicate = False
            
            for existing_char in portfolio_data.get("characters", []):
                if existing_char.get("name") == char_name:
                    duplicate = True
                    break
            
            if duplicate:
                continue
                
            # キャラクターをポートフォリオに追加
            char_info = {
                "name": char_name,
                "added_at": datetime.now().isoformat(),
                "age": char.get("age", "不明"),
                "physical_features": char.get("physical_features", ""),
                "personality": char.get("personality", ""),
                "source_setting_id": source_setting_id
            }
            
            portfolio_data["characters"].append(char_info)
        
        portfolio_data["updated_at"] = datetime.now().isoformat()
        save_portfolio(portfolio_id, portfolio_data)
        return portfolio_data
    
    # 単一のキャラクターを追加
    if character_data:
        char_name = character_data.get("name", "名前不明")
        
        # すでに同じ名前のキャラクターがポートフォリオに含まれているかチェック
        for existing_char in portfolio_data.get("characters", []):
            if existing_char.get("name") == char_name:
                return {"error": "このキャラクターはすでにポートフォリオに含まれています"}
        
        # キャラクターのタイトル（指定がなければ名前を使用）
        char_title = title if title else char_name
        
        # キャラクターをポートフォリオに追加
        char_info = {
            "id": character_id,
            "name": char_name,
            "title": char_title,
            "added_at": datetime.now().isoformat(),
            "source_setting_id": source_setting_id
        }
        
        portfolio_data["characters"].append(char_info)
        portfolio_data["updated_at"] = datetime.now().isoformat()
        
        # ポートフォリオを保存
        save_portfolio(portfolio_id, portfolio_data)
    
    return portfolio_data

def remove_from_portfolio(portfolio_id, item_id, item_type):
    """
    ポートフォリオからアイテムを削除する
    
    Args:
        portfolio_id (str): ポートフォリオID
        item_id (str): アイテムID
        item_type (str): アイテムのタイプ（"story", "setting", "character"）
        
    Returns:
        dict: 更新されたポートフォリオの情報
    """
    # ポートフォリオデータを取得
    portfolio_data = load_portfolio(portfolio_id)
    if not portfolio_data:
        return {"error": "指定されたポートフォリオが見つかりません"}
    
    # アイテムを削除
    if item_type == "story":
        portfolio_data["stories"] = [s for s in portfolio_data.get("stories", []) if s.get("id") != item_id]
    elif item_type == "setting":
        portfolio_data["settings"] = [s for s in portfolio_data.get("settings", []) if s.get("id") != item_id]
    elif item_type == "character":
        if item_id.isdigit():  # インデックスによる削除
            idx = int(item_id)
            if 0 <= idx < len(portfolio_data.get("characters", [])):
                portfolio_data["characters"].pop(idx)
        else:  # IDによる削除
            portfolio_data["characters"] = [c for c in portfolio_data.get("characters", []) if c.get("id") != item_id]
    else:
        return {"error": "無効なアイテムタイプです"}
    
    portfolio_data["updated_at"] = datetime.now().isoformat()
    
    # ポートフォリオを保存
    save_portfolio(portfolio_id, portfolio_data)
    
    return portfolio_data

def export_portfolio(portfolio_id, export_format="json"):
    """
    ポートフォリオをエクスポートする
    
    Args:
        portfolio_id (str): ポートフォリオID
        export_format (str): エクスポート形式（"json", "txt"）
        
    Returns:
        dict: エクスポート情報
    """
    # ポートフォリオデータを取得
    portfolio_data = load_portfolio(portfolio_id)
    if not portfolio_data:
        return {"error": "指定されたポートフォリオが見つかりません"}
    
    # エクスポートディレクトリを作成
    export_dir = os.path.join("data", "exports", portfolio_id)
    os.makedirs(export_dir, exist_ok=True)
    
    if export_format == "json":
        # JSONとしてエクスポート
        export_path = os.path.join(export_dir, f"{portfolio_data.get('title', 'portfolio')}.json")
        
        # 物語の内容を組み込む
        full_portfolio = dict(portfolio_data)
        full_stories = []
        
        for story_info in portfolio_data.get("stories", []):
            story_id = story_info.get("id")
            story_data = story_service.load_story(story_id)
            if story_data:
                full_story = dict(story_info)
                full_story["content"] = story_data.get("text", "")
                full_stories.append(full_story)
        
        full_portfolio["full_stories"] = full_stories
        
        # 設定の内容を組み込む
        full_settings = []
        
        for setting_info in portfolio_data.get("settings", []):
            setting_id = setting_info.get("id")
            setting_data = setting_service.load_setting(setting_id)
            if setting_data:
                full_setting = dict(setting_info)
                full_setting["data"] = setting_data
                full_settings.append(full_setting)
        
        full_portfolio["full_settings"] = full_settings
        
        # 完全なポートフォリオをJSONとして保存
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(full_portfolio, f, ensure_ascii=False, indent=2)
        
        return {
            "path": export_path,
            "format": "json",
            "size": os.path.getsize(export_path)
        }
    
    elif export_format == "txt":
        # テキストとしてエクスポート
        export_path = os.path.join(export_dir, f"{portfolio_data.get('title', 'portfolio')}.txt")
        
        with open(export_path, 'w', encoding='utf-8') as f:
            # ポートフォリオ情報
            f.write(f"# {portfolio_data.get('title', 'ポートフォリオ')}\n\n")
            f.write(f"説明: {portfolio_data.get('description', '')}\n")
            f.write(f"作成日: {portfolio_data.get('created_at', '')}\n")
            f.write(f"更新日: {portfolio_data.get('updated_at', '')}\n\n")
            
            # 物語リスト
            f.write("## 収録物語\n\n")
            for i, story_info in enumerate(portfolio_data.get("stories", [])):
                f.write(f"### {i+1}. {story_info.get('title', '無題')}\n\n")
                
                # 物語の内容を取得
                story_id = story_info.get("id")
                story_data = story_service.load_story(story_id)
                if story_data:
                    f.write(f"{story_data.get('text', '')}\n\n")
                else:
                    f.write("（物語データが見つかりません）\n\n")
            
            # 設定リスト
            f.write("## 設定リスト\n\n")
            for i, setting_info in enumerate(portfolio_data.get("settings", [])):
                f.write(f"### {i+1}. {setting_info.get('title', '無題の設定')}\n\n")
                
                # 設定の内容を取得
                setting_id = setting_info.get("id")
                setting_data = setting_service.load_setting(setting_id)
                if setting_data:
                    # キャラクター情報
                    f.write("#### 登場人物\n\n")
                    for char in setting_data.get("characters", []):
                        f.write(f"- {char.get('name', '名前不明')} ({char.get('age', '')}): ")
                        f.write(f"{char.get('physical_features', '')}, {char.get('personality', '')}\n")
                    
                    f.write("\n#### 舞台設定\n\n")
                    f.write(f"場所: {setting_data.get('setting', {}).get('location', '')}\n")
                    f.write(f"時代: {setting_data.get('setting', {}).get('era', '')}\n\n")
                    
                    f.write("#### 背景\n\n")
                    f.write(f"{setting_data.get('background', {}).get('relationship', '')}\n\n")
                else:
                    f.write("（設定データが見つかりません）\n\n")
            
            # キャラクターリスト
            f.write("## キャラクターリスト\n\n")
            for i, char_info in enumerate(portfolio_data.get("characters", [])):
                f.write(f"### {i+1}. {char_info.get('name', '名前不明')}\n\n")
                if "age" in char_info:
                    f.write(f"年齢: {char_info.get('age', '')}\n")
                if "physical_features" in char_info:
                    f.write(f"身体的特徴: {char_info.get('physical_features', '')}\n")
                if "personality" in char_info:
                    f.write(f"性格: {char_info.get('personality', '')}\n")
                f.write("\n")
        
        return {
            "path": export_path,
            "format": "txt",
            "size": os.path.getsize(export_path)
        }
    
    else:
        return {"error": "サポートされていないエクスポート形式です"}

def duplicate_story(story_id, new_title=None):
    """
    物語を複製する
    
    Args:
        story_id (str): 複製する物語ID
        new_title (str, optional): 新しい物語のタイトル
        
    Returns:
        dict: 複製された物語の情報
    """
    # 物語データを取得
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    # 新しいIDを生成
    new_id = str(uuid.uuid4())
    
    # データを複製
    duplicated_data = dict(story_data)
    
    # タイムスタンプ更新
    duplicated_data["duplicated_from"] = story_id
    duplicated_data["duplicated_at"] = datetime.now().isoformat()
    
    # カスタムタイトルがあれば設定
    if new_title:
        duplicated_data["custom_title"] = new_title
    
    # 複製されたデータを保存
    story_service.save_story(new_id, duplicated_data)
    
    return {
        "id": new_id,
        "original_id": story_id,
        "chapter": duplicated_data.get("chapter", 1),
        "style": duplicated_data.get("style", "murakami"),
        "title": new_title or f"「{duplicated_data.get('chapter', 1)}章」の複製"
    }

def save_portfolio(portfolio_id, portfolio_data):
    """ポートフォリオをファイルに保存する"""
    filepath = os.path.join("data", "portfolios", f"{portfolio_id}.json")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(portfolio_data, f, ensure_ascii=False, indent=2)
    
    return filepath

def load_portfolio(portfolio_id):
    """ポートフォリオをファイルから読み込む"""
    filepath = os.path.join("data", "portfolios", f"{portfolio_id}.json")
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        portfolio_data = json.load(f)
    
    return portfolio_data

def list_portfolios():
    """すべてのポートフォリオをリストアップする"""
    portfolio_dir = os.path.join("data", "portfolios")
    os.makedirs(portfolio_dir, exist_ok=True)
    
    portfolios = []
    for filename in os.listdir(portfolio_dir):
        if filename.endswith(".json"):
            portfolio_id = filename[:-5]  # .jsonを除去
            portfolio_data = load_portfolio(portfolio_id)
            if portfolio_data:
                portfolio_summary = {
                    "id": portfolio_id,
                    "title": portfolio_data.get("title", "無題"),
                    "description": portfolio_data.get("description", ""),
                    "created_at": portfolio_data.get("created_at", ""),
                    "updated_at": portfolio_data.get("updated_at", ""),
                    "story_count": len(portfolio_data.get("stories", [])),
                    "setting_count": len(portfolio_data.get("settings", [])),
                    "character_count": len(portfolio_data.get("characters", []))
                }
                portfolios.append(portfolio_summary)
    
    # 更新日時の降順でソート
    portfolios.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    
    return portfolios

def search_portfolio(query, portfolio_id=None):
    """
    ポートフォリオ内のコンテンツを検索する
    
    Args:
        query (str): 検索クエリ
        portfolio_id (str, optional): 特定のポートフォリオID（指定なしの場合はすべてのポートフォリオを検索）
        
    Returns:
        dict: 検索結果
    """
    if not query:
        return {"error": "検索クエリが指定されていません"}
    
    query = query.lower()
    results = {
        "stories": [],
        "settings": [],
        "characters": []
    }
    
    # 検索対象のポートフォリオリスト
    portfolios_to_search = []
    if portfolio_id:
        portfolio_data = load_portfolio(portfolio_id)
        if portfolio_data:
            portfolios_to_search.append(portfolio_data)
    else:
        portfolio_dir = os.path.join("data", "portfolios")
        if os.path.exists(portfolio_dir):
            for filename in os.listdir(portfolio_dir):
                if filename.endswith(".json"):
                    p_id = filename[:-5]
                    p_data = load_portfolio(p_id)
                    if p_data:
                        portfolios_to_search.append(p_data)
    
    # 各ポートフォリオを検索
    for portfolio in portfolios_to_search:
        portfolio_id = portfolio.get("id", "unknown")
        
        # 物語を検索
        for story_info in portfolio.get("stories", []):
            story_id = story_info.get("id")
            if story_id:
                story_data = story_service.load_story(story_id)
                if story_data:
                    story_text = story_data.get("text", "").lower()
                    story_title = story_info.get("title", "").lower()
                    
                    if query in story_text or query in story_title:
                        # 検索結果のプレビューを作成
                        preview = ""
                        if query in story_text:
                            query_pos = story_text.find(query)
                            start_pos = max(0, query_pos - 50)
                            end_pos = min(len(story_text), query_pos + len(query) + 50)
                            preview = f"...{story_text[start_pos:end_pos]}..."
                        
                        results["stories"].append({
                            "id": story_id,
                            "title": story_info.get("title", "無題"),
                            "portfolio_id": portfolio_id,
                            "preview": preview
                        })
        
        # 設定を検索
        for setting_info in portfolio.get("settings", []):
            setting_id = setting_info.get("id")
            if setting_id:
                setting_data = setting_service.load_setting(setting_id)
                if setting_data:
                    # キャラクター情報を検索
                    for char in setting_data.get("characters", []):
                        char_name = char.get("name", "").lower()
                        char_features = char.get("physical_features", "").lower()
                        char_personality = char.get("personality", "").lower()
                        
                        if (query in char_name or query in char_features or 
                            query in char_personality):
                            results["characters"].append({
                                "name": char.get("name", "名前不明"),
                                "setting_id": setting_id,
                                "portfolio_id": portfolio_id,
                                "setting_title": setting_info.get("title", "無題の設定")
                            })
                    
                    # 設定の他の情報を検索
                    setting_location = setting_data.get("setting", {}).get("location", "").lower()
                    setting_era = setting_data.get("setting", {}).get("era", "").lower()
                    setting_background = setting_data.get("background", {}).get("relationship", "").lower()
                    
                    if (query in setting_location or query in setting_era or 
                        query in setting_background):
                        results["settings"].append({
                            "id": setting_id,
                            "title": setting_info.get("title", "無題の設定"),
                            "portfolio_id": portfolio_id
                        })
        
        # ポートフォリオ内のキャラクターを検索
        for char_info in portfolio.get("characters", []):
            char_name = char_info.get("name", "").lower()
            char_features = char_info.get("physical_features", "").lower()
            char_personality = char_info.get("personality", "").lower()
            
            if query in char_name or query in char_features or query in char_personality:
                results["characters"].append({
                    "name": char_info.get("name", "名前不明"),
                    "portfolio_id": portfolio_id
                })
    
    # 結果の合計数を追加
    results["total_count"] = len(results["stories"]) + len(results["settings"]) + len(results["characters"])
    
    return results