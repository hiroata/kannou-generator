import os
import json
import uuid
from api import grok_api
from services import story_service, setting_service, synopsis_service

def enhance_character_psychology(story_text, character_data):
    """キャラクターの心理描写を強化する"""
    prompt = f"""
    以下の官能小説の文章を、登場人物の内面や心理をより深く掘り下げたバージョンに書き換えてください。
    
    原文:
    {story_text}
    
    登場人物情報:
    {json.dumps(character_data, ensure_ascii=False)}
    
    以下の要素を強化してください:
    1. 性的な行為に至るまでの内面の葛藤や欲望の成長過程
    2. 禁断の感情や背徳感、罪悪感と快感の葛藤
    3. 相手に対する複雑な感情（愛情/憎悪/嫉妬/執着など）
    4. 過去のトラウマや経験が現在の行動に与える影響
    5. 社会的立場や周囲の目を気にする心理
    
    ただし、以下の点は必ず維持してください:
    1. 卑猥な淫語セリフや露骨な性描写
    2. 原文の展開やシチュエーション
    3. キャラクターの基本的な性格
    
    文字数は原文の1.2〜1.5倍程度に拡張してください。
    過激で卑猥な表現を多用し、読者の興奮を極限まで高めてください。
    """
    
    enhanced_text = grok_api.generate_text(prompt, max_tokens=7000, temperature=0.9)
    return enhanced_text

def enhance_emotional_arc(story_text):
    """ストーリーの感情的な起伏を強化する"""
    prompt = f"""
    以下の官能小説について、感情的な起伏とドラマ性を強化した改訂版を作成してください。
    
    原文:
    {story_text}
    
    以下の要素を強化してください:
    1. テンションの上下：期待→挫折→再挑戦→成功、といった感情の波を作る
    2. 予想外の展開：読者の予想を裏切る意外な展開やどんでん返し
    3. 葛藤と解決：主人公が直面する内的/外的な障害とその克服過程
    4. 感情的なピーク：読者が最も感情移入できる山場の強化
    5. 余韻のある終わり：読者の心に残るエンディングまたは次章への期待感
    
    ただし、以下の点は必ず維持してください:
    1. 卑猥なセリフや性描写の具体性と直接性
    2. キャラクターの設定や関係性の一貫性
    3. 基本的なストーリーの流れ
    
    文体や表現の露骨さはそのままに、より感情的な深みと読み応えのある内容にしてください。
    過激で卑猥な表現を多用し、読者の興奮を極限まで高めてください。
    """
    
    enhanced_text = grok_api.generate_text(prompt, max_tokens=7000, temperature=0.9)
    return enhanced_text

def enhance_sensory_descriptions(story_text):
    """五感的な描写を強化する"""
    prompt = f"""
    以下の官能小説の文章に、五感を活用したより豊かな描写を加えてください。
    
    原文:
    {story_text}
    
    以下の感覚的要素を追加・強化してください:
    1. 視覚：色彩、光と影、細部の描写
    2. 聴覚：喘ぎ声、囁き、肌と肌が触れ合う音、環境音
    3. 触覚：皮膚感覚、温度、質感、圧力、痛みと快感
    4. 嗅覚：体臭、香水、汗の匂い、性的な匂い
    5. 味覚：キス、体液、肌の味
    
    特に以下の点を重視してください:
    1. 性的な行為の最中の感覚的体験をより鮮明に
    2. キャラクターの体の反応や生理的変化を詳細に
    3. 環境や場所の雰囲気を感覚的に伝える
    4. 性的興奮の高まりを感覚的変化で表現
    
    卑猥な表現や淫語は維持しつつ、より官能的で没入感のある描写にしてください。
    過激で卑猥な表現を多用し、読者の興奮を極限まで高めてください。
    """
    
    enhanced_text = grok_api.generate_text(prompt, max_tokens=7000, temperature=0.9)
    return enhanced_text

def enhance_character_voice(story_text, character_data):
    """キャラクターごとの話し方・思考パターンを一貫させる"""
    prompt = f"""
    以下の官能小説におけるキャラクターの「声」（話し方、言葉遣い、思考パターン）を
    より一貫性のあるものに強化してください。
    
    小説:
    {story_text}
    
    登場人物情報:
    {json.dumps(character_data, ensure_ascii=False)}
    
    各キャラクターについて以下の要素を一貫させてください:
    1. 特徴的な言葉遣いや口癖
    2. 性的興奮時の特徴的な喘ぎ声やセリフパターン
    3. 内面の思考を表現する文体
    4. 社会的立場や教育背景に合った話し方
    5. 感情状態による言葉遣いの変化パターン
    
    特に性的なシーンでの台詞については:
    1. キャラクターの性格に合った淫語表現の選択
    2. 興奮度合いによる言葉遣いの変化
    3. 性的嗜好を反映した表現の使い分け
    
    キャラクターの個性をより鮮明に表現しつつ、卑猥な表現は維持または強化してください。
    過激で卑猥な表現を多用し、読者の興奮を極限まで高めてください。
    """
    
    enhanced_text = grok_api.generate_text(prompt, max_tokens=7000, temperature=0.9)
    return enhanced_text

def add_psychological_themes(story_text):
    """ストーリーに心理学的なテーマや象徴を追加する"""
    prompt = f"""
    以下の官能小説に、深層心理学的なテーマや象徴性を追加してください。
    卑猥な表現はそのままに、ストーリーに奥行きと多層性を与えてください。
    
    小説:
    {story_text}
    
    以下の要素を追加または強化してください:
    1. ユング心理学的な元型やシンボルの活用
    2. フロイト的な欲望と抑圧の葛藤
    3. トラウマや心の傷の表現と癒し
    4. 社会的タブーと個人の欲望の対立
    5. 権力関係や支配/被支配の心理的力学
    
    以下の点に注意してください:
    1. 性描写の生々しさは維持しつつ、その行為の象徴的な意味も示唆する
    2. 官能表現に心理的な深みを加える
    3. キャラクターの行動の裏にある無意識的動機を暗示する
    4. 性的シーンをより広いテーマの文脈に位置づける
    
    露骨な性描写と心理的深みを両立させた、より文学的な作品に仕上げてください。
    過激で卑猥な表現を多用し、読者の興奮を極限まで高めてください。
    """
    
    enhanced_text = grok_api.generate_text(prompt, max_tokens=7000, temperature=0.9)
    return enhanced_text

def generate_scene_prompts(story_text, num_scenes=3):
    """ストーリーから重要シーンを選び、SD用プロンプトを生成する"""
    prompt = f"""
    以下の官能小説から、印象的な{num_scenes}つのシーンを選び、
    各シーンをStable Diffusion用のプロンプトに変換してください。
    
    小説:
    {story_text}
    
    各シーンについて以下の要素を含めてください:
    1. シーン概要：シーンの簡潔な説明（ナレーション用）
    2. 会話/セリフ：そのシーンでの重要なセリフ（吹き出し用）
    3. 構図説明：画面構成、アングル、キャラクターの位置関係
    4. SD用ポジティブプロンプト：キャラクター外見、服装/裸体状態、行為、表情、環境、照明、画風
    5. SD用ネガティブプロンプト：避けるべき要素
    
    成人向けの絵を生成するためのプロンプトであることを前提に、
    必要な性的要素や体位、行為の詳細を具体的に含めてください。
    過激で卑猥な表現を多用し、読者の興奮を極限まで高めてください。
    
    以下の形式で出力してください：
    
    # シーン1
    ## シーン概要
    (シーンの説明)
    
    ## 会話/セリフ
    (重要なセリフ)
    
    ## 構図説明
    (構図の詳細)
    
    ## SD用ポジティブプロンプト
    (プロンプト)
    
    ## SD用ネガティブプロンプト
    (ネガティブプロンプト)
    
    # シーン2
    ...
    """
    
    return grok_api.generate_text(prompt, max_tokens=5000, temperature=0.9)

def enhance_story(story_id, options):
    """物語を複数の方法で強化する総合関数"""
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    original_text = story_data.get("text", "")
    
    setting_id = story_data.get("setting_id")
    if setting_id:
        setting_data = setting_service.load_setting(setting_id)
    else:
        synopsis_id = story_data.get("synopsis_id")
        synopsis_data = synopsis_service.load_synopsis(synopsis_id)
        setting_id = synopsis_data.get("setting_id") if synopsis_data else None
        setting_data = setting_service.load_setting(setting_id) if setting_id else {}
    
    enhanced_text = original_text
    
    if options.get("enhance_psychology", False) and setting_data:
        print("Enhancing character psychology...")
        enhanced_text = enhance_character_psychology(enhanced_text, setting_data.get("characters", []))
    
    if options.get("enhance_emotions", False):
        print("Enhancing emotional arc...")
        enhanced_text = enhance_emotional_arc(enhanced_text)
    
    if options.get("enhance_sensory", False):
        print("Enhancing sensory descriptions...")
        enhanced_text = enhance_sensory_descriptions(enhanced_text)
    
    if options.get("enhance_voice", False) and setting_data:
        print("Enhancing character voices...")
        enhanced_text = enhance_character_voice(enhanced_text, setting_data.get("characters", []))
    
    if options.get("add_psychological_themes", False):
        print("Adding psychological themes...")
        enhanced_text = add_psychological_themes(enhanced_text)
    
    enhanced_story_id = str(uuid.uuid4())
    enhanced_story_data = dict(story_data)
    enhanced_story_data["text"] = enhanced_text
    enhanced_story_data["enhanced"] = True
    enhanced_story_data["enhancement_options"] = options
    enhanced_story_data["original_story_id"] = story_id
    
    story_service.save_story(enhanced_story_id, enhanced_story_data)
    
    return {
        "id": enhanced_story_id,
        "chapter": story_data.get("chapter", 1),
        "text": enhanced_text,
        "enhanced": True
    }

def save_scene_prompts(story_id, prompts_text):
    """シーンプロンプトをファイルに保存する"""
    filepath = os.path.join("data", "prompts", f"{story_id}.txt")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(prompts_text)
    
    return filepath

def load_scene_prompts(story_id):
    """シーンプロンプトをファイルから読み込む"""
    filepath = os.path.join("data", "prompts", f"{story_id}.txt")
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        prompts_text = f.read()
    
    return prompts_text