import os
import json
import uuid
import importlib
from config import AVAILABLE_MODELS, WRITING_STYLES

def generate_story(synopsis_id, synopsis_index=0, model="grok", style="murakami", chapter=1, direction="", enhance_options=None):
    """
    あらすじに基づいて小説を生成する
    
    Args:
        synopsis_id (str): あらすじID
        synopsis_index (int): あらすじのインデックス
        model (str): 使用するモデル ('grok', 'gemini')
        style (str): 文体スタイル ('murakami' または 'dan' または 'eromanga')
        chapter (int): 生成する章番号
        direction (str): 次の章の方向性に関する指示（オプション）
        enhance_options (dict): 強化オプション
    
    Returns:
        dict: 生成された小説
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
    
    # デフォルトの強化オプション
    if enhance_options is None:
        enhance_options = {
            "explicitness_level": 6  # デフォルトで最大露骨さ
        }
    
    # あらすじの読み込み
    synopses_data = load_synopsis(synopsis_id)
    if not synopses_data:
        return {"error": "あらすじが見つかりません"}
    
    # 設定の読み込み
    from services import setting_service
    setting_id = synopses_data.get("setting_id")
    setting_data = setting_service.load_setting(setting_id)
    
    # 選択されたあらすじ
    synopses = synopses_data.get("synopses", [])
    if not isinstance(synopses, list) or synopsis_index >= len(synopses):
        return {"error": "指定されたあらすじが存在しません"}
        
    selected_synopsis = synopses[synopsis_index]
    
    # 文体の選択
    writing_style = WRITING_STYLES.get(style, WRITING_STYLES["murakami"])
    
    # 章タイプの詳細定義
    chapter_types = {
        1: {
            "name": "導入部",
            "description": "物語の舞台設定、主要な登場人物の紹介、主要な葛藤や欲望の提示。性的緊張の端緒を示す。",
            "target_length": "1000〜1500文字",
            "max_tokens": 2500
        },
        2: {
            "name": "展開部（前半）",
            "description": "第1章で示された状況から大きく展開し、新たな展開や関係性の変化を導入。性的緊張がより高まり、新たな状況や障害が発生する。導入部とは明確に異なる新展開を含める。",
            "target_length": "1200〜1800文字",
            "max_tokens": 3000
        },
        3: {
            "name": "展開部（後半）",
            "description": "葛藤や性的緊張がさらに複雑化し、予想外の障害や展開が発生。感情的な起伏が激しくなり、より深い関係性や背景が明らかになる。前章とは大きく異なる状況や場所での展開を含める。",
            "target_length": "1500〜2000文字",
            "max_tokens": 3500
        },
        4: {
            "name": "クライマックスへの加速",
            "description": "物語の緊張が最高潮に達する直前の状態。すべての伏線や関係性が収束し始め、避けられない決断や対峙が迫る。性的緊張が極限まで高まる。前章の展開を大きく進め、物語を決定的な方向へ導く。",
            "target_length": "1500〜2000文字",
            "max_tokens": 3500
        },
        5: {
            "name": "クライマックスと解決",
            "description": "物語の最も重要な瞬間、主要な葛藤の決着と感情的頂点。最も激しい性的描写や感情の爆発を含む。物語の主要な疑問に対する答えや関係性の最終的な形が明らかになる。",
            "target_length": "1800〜2500文字",
            "max_tokens": 4000
        }
    }
    
    # 範囲外の章番号の処理（6章以降は特別エピソードとして扱う）
    if chapter > 5:
        special_chapter = {
            "name": f"特別エピソード（第{chapter}章）",
            "description": f"物語の主要な山場を過ぎた後の特別な展開や発展。新たな関係性や状況の探索、または以前の章で示された伏線の発展。完全に新しい展開や視点を導入し、物語に新たな息吹を吹き込む。第{chapter-1}章とは全く異なる展開を心がける。",
            "target_length": "1500〜2000文字",
            "max_tokens": 3500
        }
        chapter_types[chapter] = special_chapter
    
    # 現在の章のタイプ情報を取得
    current_chapter_type = chapter_types.get(chapter, chapter_types[5])
    chapter_part = current_chapter_type["name"]
    chapter_description = current_chapter_type["description"]
    target_length = current_chapter_type["target_length"]
    max_tokens = current_chapter_type["max_tokens"]
    
    # 露骨さレベルの設定
    explicitness_level = enhance_options.get("explicitness_level", 6)
    explicitness_instruction = "極端に露骨で異常。性的内容を異常なまでに詳細かつ過激に描写し、卑猥な言葉や淫語を極限まで多用。読者の興奮を極端に煽る表現を追求。"
    
    # 前章の詳細要約を取得
    previous_chapter_summary = ""
    previous_chapter_full = ""
    if chapter > 1:
        previous_chapter_result = get_previous_chapter_detail(synopsis_id, synopsis_index, chapter - 1)
        previous_chapter_summary = previous_chapter_result.get("summary", "")
        previous_chapter_full = previous_chapter_result.get("full_text", "")
    
    # 方向性指示（ユーザー入力）
    direction_instruction = f"次の章の方向性: {direction}" if direction else ""
    
    # プロンプトの作成 - 章ごとの特性を強化
    prompt = f"""
    あなたは18禁官能小説の作家です。以下の設定、あらすじ、これまでの展開に基づいて、{writing_style}で第{chapter}章（{chapter_part}）を執筆してください。
    
    設定: {json.dumps(setting_data, ensure_ascii=False)}
    
    あらすじの概要: {json.dumps(selected_synopsis, ensure_ascii=False)}
    
    章の特性: {chapter_description}
    
    ===前章までの展開===
    {previous_chapter_summary}
    
    {direction_instruction}
    
    露骨さレベル: {explicitness_level} - {explicitness_instruction}
    
    文学的表現に関する特別指示:
    1. 又吉直樹や谷崎潤一郎のような純文学的な文体で地の文を書いてください。
    2. 年齢、身長、バストサイズなどの身体的特徴を数値で表現せず、比喩や暗示的な表現で読者の想像力を刺激してください。
    3. 例えば「28歳」→「二十代後半の」、「180cm」→「頭一つ以上背の高い」、「20cm」→「常軌を逸した大きさの」など。
    4. 感覚的、象徴的、比喩的な表現を多用し、直接的な数値表現を避けてください。
    5. キャラクターの身体的特徴は見た目や雰囲気、質感、そして他者との対比で表現してください。
    
    ストーリー展開に関する重要な指示:
    1. 第{chapter}章として、明確に前章から続く物語を展開してください。前章の出来事を受けて、物語を大きく前進させてください。
    2. 前章とは異なる場面、状況、感情を描写し、完全に新しい展開を導入してください。同じような状況の繰り返しは避けてください。
    3. キャラクターの関係性に明確な変化や進展を示してください。
    4. この章だけの独自の展開、葛藤、障害、または状況を導入してください。
    5. 読者を驚かせるような予想外の展開や視点の変化を含めてください。
    6. 前章で示された伏線を回収するか、新たな伏線を張ってください。
    
    注意点:
    1. 官能的な描写は詳細かつ生々しく、卑猥な表現を多用。
    2. 喘ぎ声（「あぁん」「んっ」）や淫語（「チンポ」「マンコ」）を積極的に使用。
    3. 心理描写と身体的反応を鮮明に表現。
    4. 日本のエロ同人マンガ風のオノマトペ（ズチュッ、グチョッ）を多用。
    5. 文字数は{target_length}程度。
    
    この章は前章から続く物語の一部であり、物語を大きく前進させる新しい展開を含めることが非常に重要です。前章の展開を踏まえつつ、物語全体を新たな方向へと導く章にしてください。同じ状況の繰り返しは厳禁です。
    
    章のタイトルをつけ、改行を適切に使用して読みやすくしてください。
    """
    
    # API呼び出し
    story_text = api_module.generate_text(prompt, max_tokens=max_tokens, temperature=0.9)
    
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
        "enhance_options": enhance_options,
        "text": story_text,
        "previous_chapter_summary": previous_chapter_summary
    })
    
    return {
        "id": story_id,
        "chapter": chapter,
        "text": story_text
    }

def get_previous_chapter_detail(synopsis_id, synopsis_index, chapter):
    """前章の詳細情報と要約を取得する"""
    story_dir = os.path.join("data", "stories")
    previous_chapter_text = ""
    previous_chapter_id = None
    
    if os.path.exists(story_dir):
        # 最新の適切な章を探す（同じあらすじと章番号を持つ）
        matching_stories = []
        
        for filename in os.listdir(story_dir):
            if filename.endswith(".json"):
                story_path = os.path.join(story_dir, filename)
                try:
                    with open(story_path, 'r', encoding='utf-8') as f:
                        story_data = json.load(f)
                        if (story_data.get("synopsis_id") == synopsis_id and 
                            story_data.get("synopsis_index") == synopsis_index and
                            story_data.get("chapter") == chapter):
                            # 作成時間（またはファイル更新時間）でソートできるようにタイムスタンプを取得
                            file_timestamp = os.path.getmtime(story_path)
                            matching_stories.append({
                                "id": filename.replace(".json", ""),
                                "text": story_data.get("text", ""),
                                "timestamp": file_timestamp,
                                "model": story_data.get("model", "grok")
                            })
                except Exception as e:
                    print(f"Error loading story {filename}: {e}")
        
        # タイムスタンプで降順にソート（最新のものが先頭に）
        matching_stories.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # 最新のものを使用
        if matching_stories:
            previous_chapter_text = matching_stories[0]["text"]
            previous_chapter_id = matching_stories[0]["id"]
            previous_chapter_model = matching_stories[0]["model"]
    
    # 前章が見つかれば、詳細な要約を生成
    if previous_chapter_text:
        # APIモジュールの動的インポート
        api_module_name = AVAILABLE_MODELS.get(previous_chapter_model, AVAILABLE_MODELS["grok"])["api_module"]
        try:
            api_module = importlib.import_module(f"api.{api_module_name}")
        except ImportError:
            print(f"APIモジュール {api_module_name} のインポートに失敗しました")
            api_module_name = "grok_api"
            api_module = importlib.import_module(f"api.{api_module_name}")
        
        # 詳細な要約を生成 - 500文字程度の十分な長さに
        summary_prompt = f"""
        以下の物語の前の章を詳細に要約してください。次の章を書くために必要な情報を含めてください。
        
        以下の要素を必ず含めてください:
        1. 主要な出来事と展開（少なくとも3つ）
        2. キャラクター同士の関係性の変化や進展
        3. 性的な緊張や行為の内容と結果
        4. 感情の起伏や心理的な変化
        5. 次の章で解決または発展させるべき未解決の問題や伏線
        
        要約は800文字程度で作成し、次の章の執筆に役立つ具体的な情報を含めてください。
        
        物語:
        {previous_chapter_text}
        """
        
        summary = api_module.generate_text(summary_prompt, max_tokens=1500, temperature=0.7)
        
        return {
            "id": previous_chapter_id,
            "summary": summary,
            "full_text": previous_chapter_text
        }
    
    return {
        "summary": "",
        "full_text": ""
    }

def save_story(story_id, story_data):
    """小説をファイルに保存する"""
    filepath = os.path.join("data", "stories", f"{story_id}.json")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
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

def load_synopsis(synopsis_id):
    """あらすじをファイルから読み込む"""
    # synopsis_service から直接インポートするとcircular importになる可能性があるため、ここでファイルから読み込む
    filepath = os.path.join("data", "synopses", f"{synopsis_id}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        synopses_data = json.load(f)
    return synopses_data