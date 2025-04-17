import os
import json
import uuid
from api import grok_api
from services import setting_service, synopsis_service
from config import WRITING_STYLES

def generate_story(synopsis_id, synopsis_index=0, model="grok", style="murakami", chapter=1, direction="", enhance_options=None):
    """
    あらすじに基づいて小説を生成する
    
    Args:
        synopsis_id (str): あらすじID
        synopsis_index (int): あらすじのインデックス
        model (str): 使用するモデル（'grok'のみサポート）
        style (str): 文体スタイル ('murakami' または 'dan' または 'eromanga')
        chapter (int): 生成する章番号
        direction (str): 次の章の方向性に関する指示（オプション）
        enhance_options (dict): 強化オプション
    
    Returns:
        dict: 生成された小説
    """
    # デフォルトの強化オプション
    if enhance_options is None:
        enhance_options = {
            "explicitness_level": 6  # デフォルトで最大露骨さ
        }
    
    # モデルはGrokに固定
    model = "grok"
    
    # あらすじの読み込み
    synopses_data = synopsis_service.load_synopsis(synopsis_id)
    if not synopses_data:
        return {"error": "あらすじが見つかりません"}
    
    # 設定の読み込み
    setting_id = synopses_data.get("setting_id")
    setting_data = setting_service.load_setting(setting_id)
    
    # 選択されたあらすじ
    synopses = synopses_data.get("synopses", [])
    if not isinstance(synopses, list) or synopsis_index >= len(synopses):
        return {"error": "指定されたあらすじが存在しません"}
        
    selected_synopsis = synopses[synopsis_index]
    
    # 文体の選択
    writing_style = WRITING_STYLES.get(style, WRITING_STYLES["murakami"])
    
    # 章に応じた設定
    if chapter == 1:
        story_part = "導入部"
        target_length = "700〜1000文字"
        max_tokens = 2000
    elif chapter == 2:
        story_part = "展開部"
        target_length = "700〜1000文字"
        max_tokens = 2500
    elif chapter == 3:
        story_part = "クライマックスと結末"
        target_length = "800〜1200文字"
        max_tokens = 3000
    else:
        story_part = "追加エピソード"
        target_length = "800〜1200文字"
        max_tokens = 3000
    
    # 露骨さレベルの設定
    explicitness_level = enhance_options.get("explicitness_level", 6)
    explicitness_instruction = "極端に露骨で異常。性的内容を異常なまでに詳細かつ過激に描写し、卑猥な言葉や淫語を極限まで多用。読者の興奮を極端に煽る表現を追求。"
    
    # 前章の要約を取得
    previous_chapter_summary = ""
    if chapter > 1:
        previous_chapter_summary = get_previous_chapter_summary(synopsis_id, synopsis_index, chapter - 1)
    
    # 方向性指示
    direction_instruction = f"次の章の方向性: {direction}" if direction else ""
    
    # プロンプトの作成
    prompt = f"""
    あなたは18禁官能小説の作家です。以下の設定とあらすじに基づいて、{writing_style}で第{chapter}章（{story_part}）を執筆してください。
    
    設定: {json.dumps(setting_data, ensure_ascii=False)}
    あらすじ: {json.dumps(selected_synopsis, ensure_ascii=False)}
    {f"前章の要約: {previous_chapter_summary}" if previous_chapter_summary else ""}
    {direction_instruction}
    露骨さレベル: {explicitness_level} - {explicitness_instruction}
    
    文学的表現に関する特別指示:
    1. 又吉直樹や谷崎潤一郎のような純文学的な文体で地の文を書いてください。
    2. 年齢、身長、バストサイズなどの身体的特徴を数値で表現せず、比喩や暗示的な表現で読者の想像力を刺激してください。
    3. 例えば「28歳」→「二十代後半の」、「180cm」→「頭一つ以上背の高い」、「20cm」→「常軌を逸した大きさの」など。
    4. 感覚的、象徴的、比喩的な表現を多用し、直接的な数値表現を避けてください。
    5. キャラクターの身体的特徴は見た目や雰囲気、質感、そして他者との対比で表現してください。
    
    注意点:
    1. 官能的な描写は詳細かつ生々しく、卑猥な表現を多用。
    2. 喘ぎ声（「あぁん」「んっ」）や淫語（「チンポ」「マンコ」）を積極的に使用。
    3. 心理描写と身体的反応を鮮明に表現。
    4. 日本のエロ同人マンガ風のオノマトペ（ズチュッ、グチョッ）を多用。
    5. 文字数は{target_length}程度。
    
    章のタイトルをつけ、改行を適切に使用して読みやすくしてください。
    """
    
    # Grok API呼び出し
    story_text = grok_api.generate_text(prompt, max_tokens=max_tokens, temperature=0.9)
    
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
        "text": story_text
    })
    
    return {
        "id": story_id,
        "chapter": chapter,
        "text": story_text
    }

def get_previous_chapter_summary(synopsis_id, synopsis_index, chapter):
    """前章の要約を取得する"""
    story_dir = os.path.join("data", "stories")
    previous_chapter_text = ""
    
    if os.path.exists(story_dir):
        for filename in os.listdir(story_dir):
            if filename.endswith(".json"):
                story_path = os.path.join(story_dir, filename)
                try:
                    with open(story_path, 'r', encoding='utf-8') as f:
                        story_data = json.load(f)
                        if (story_data.get("synopsis_id") == synopsis_id and 
                            story_data.get("synopsis_index") == synopsis_index and
                            story_data.get("chapter") == chapter):
                            previous_chapter_text = story_data.get("text", "")
                            break
                except Exception as e:
                    print(f"Error loading story {filename}: {e}")
    
    if previous_chapter_text:
        # 要約を生成
        summary_prompt = f"以下の物語の要約を100文字以内で作成してください:\n\n{previous_chapter_text}"
        summary = grok_api.generate_text(summary_prompt, max_tokens=200, temperature=0.7)
        return summary
    return ""

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