import os
import json
import uuid
from api import grok_api
from services import story_service

def enhance_selected_section(story_id, section_start, section_end, enhancement_type="sensory", intensity=3):
    """
    物語の選択された部分を強化する
    
    Args:
        story_id (str): 物語ID
        section_start (str): セクションの開始部分（数文字〜数十文字）
        section_end (str): セクションの終了部分（数文字〜数十文字）
        enhancement_type (str): 強化のタイプ
            - "sensory": 感覚的な描写を強化
            - "psychological": 心理描写を強化
            - "erotic": 官能描写を強化
            - "emotional": 感情描写を強化
            - "action": 行動描写を強化
            - "dialogue": 会話を強化
        intensity (int): 強化の強度（1-5）
            
    Returns:
        dict: 強化された物語
    """
    # 物語データを取得
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    # 物語のテキスト
    story_text = story_data.get("text", "")
    
    # セクションの抽出
    try:
        start_index = story_text.index(section_start)
        end_index = story_text.index(section_end, start_index) + len(section_end)
        selected_section = story_text[start_index:end_index]
    except ValueError:
        return {"error": "指定されたセクションが見つかりません"}
    
    # 強化タイプの説明
    enhancement_descriptions = {
        "sensory": "五感（視覚、聴覚、触覚、嗅覚、味覚）を使った描写を強化し、より没入感のあるシーンにする。",
        "psychological": "登場人物の内面、思考プロセス、葛藤、欲望などの心理描写を深める。",
        "erotic": "性的な描写の質と深さを高め、より官能的で刺激的なシーンにする。",
        "emotional": "感情表現を豊かにし、キャラクターの感情の起伏をより鮮明に描く。",
        "action": "行動や動きの描写を詳細にし、テンポや緊張感を高める。",
        "dialogue": "会話の質を向上させ、キャラクターの個性や関係性をより明確に示す。"
    }
    
    enhancement_desc = enhancement_descriptions.get(enhancement_type, "標準的な強化")
    
    prompt = f"""
    以下の官能小説の選択された部分を、「{enhancement_type}」タイプの強化で改善してください。
    
    選択されたセクション:
    {selected_section}
    
    強化タイプ: {enhancement_type}
    説明: {enhancement_desc}
    強度: {intensity}（1は微妙な変化、5は大幅な強化）
    
    以下の条件に従って強化してください:
    1. セクションの基本的な内容や流れは維持する
    2. 指定された強化タイプに沿った改善を行う
    3. 強化の強度を指定されたレベルにする
    4. 文体や全体のトーンとの一貫性を保つ
    5. セクションの長さを大幅に変えない
    6. 村上龍のようなハードボイルドで都会的な描写を心がける
    7. 数値的なサイズの言及は避け、文学的表現を用いる
    
    強化されたセクションのみを返してください。
    """
    
    # API呼び出し
    enhanced_section = grok_api.generate_text(prompt, max_tokens=len(selected_section) * 1.5)
    
    # 元の物語に強化されたセクションを組み込む
    enhanced_text = story_text[:start_index] + enhanced_section + story_text[end_index:]
    
    # 結果をフォーマット
    enhanced_story = dict(story_data)
    enhanced_story["text"] = enhanced_text
    enhanced_story["section_enhancement"] = {
        "section_start": section_start[:50] + "..." if len(section_start) > 50 else section_start,
        "section_end": section_end[:50] + "..." if len(section_end) > 50 else section_end,
        "enhancement_type": enhancement_type,
        "intensity": intensity
    }
    
    # 強化された物語の保存
    enhanced_id = str(uuid.uuid4())
    story_service.save_story(enhanced_id, enhanced_story)
    
    return {
        "id": enhanced_id,
        "chapter": enhanced_story.get("chapter", 1),
        "text": enhanced_text,
        "enhanced_section": enhanced_section,
        "enhancement_type": enhancement_type
    }

def rewrite_section_with_prompt(story_id, section_start, section_end, custom_prompt):
    """
    カスタムプロンプトに基づいて物語の選択された部分を書き換える
    
    Args:
        story_id (str): 物語ID
        section_start (str): セクションの開始部分（数文字〜数十文字）
        section_end (str): セクションの終了部分（数文字〜数十文字）
        custom_prompt (str): カスタム指示プロンプト
            
    Returns:
        dict: 書き換えられた物語
    """
    # 物語データを取得
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    # 物語のテキスト
    story_text = story_data.get("text", "")
    
    # セクションの抽出
    try:
        start_index = story_text.index(section_start)
        end_index = story_text.index(section_end, start_index) + len(section_end)
        selected_section = story_text[start_index:end_index]
    except ValueError:
        return {"error": "指定されたセクションが見つかりません"}
    
    prompt = f"""
    以下の官能小説の選択された部分を、指定された指示に基づいて書き換えてください。
    
    選択されたセクション:
    {selected_section}
    
    指示:
    {custom_prompt}
    
    以下の条件に従って書き換えてください:
    1. 指定された指示を可能な限り忠実に反映する
    2. 物語全体との一貫性を保つ
    3. 文体やトーンを維持する
    4. 村上龍のようなハードボイルドで都会的な表現を使用する
    5. 数値的な身体描写は避け、文学的表現を用いる
    
    書き換えられたセクションのみを返してください。
    """
    
    # API呼び出し
    rewritten_section = grok_api.generate_text(prompt, max_tokens=len(selected_section) * 1.5)
    
    # 元の物語に書き換えられたセクションを組み込む
    rewritten_text = story_text[:start_index] + rewritten_section + story_text[end_index:]
    
    # 結果をフォーマット
    rewritten_story = dict(story_data)
    rewritten_story["text"] = rewritten_text
    rewritten_story["section_rewrite"] = {
        "section_start": section_start[:50] + "..." if len(section_start) > 50 else section_start,
        "section_end": section_end[:50] + "..." if len(section_end) > 50 else section_end,
        "custom_prompt": custom_prompt
    }
    
    # 書き換えられた物語の保存
    rewritten_id = str(uuid.uuid4())
    story_service.save_story(rewritten_id, rewritten_story)
    
    return {
        "id": rewritten_id,
        "chapter": rewritten_story.get("chapter", 1),
        "text": rewritten_text,
        "rewritten_section": rewritten_section
    }

def expand_section(story_id, section_start, section_end, expansion_factor=2.0):
    """
    物語の選択された部分を拡張する
    
    Args:
        story_id (str): 物語ID
        section_start (str): セクションの開始部分（数文字〜数十文字）
        section_end (str): セクションの終了部分（数文字〜数十文字）
        expansion_factor (float): 拡張係数（1.0より大きい値）
            
    Returns:
        dict: 拡張された物語
    """
    # 物語データを取得
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    # 物語のテキスト
    story_text = story_data.get("text", "")
    
    # セクションの抽出
    try:
        start_index = story_text.index(section_start)
        end_index = story_text.index(section_end, start_index) + len(section_end)
        selected_section = story_text[start_index:end_index]
    except ValueError:
        return {"error": "指定されたセクションが見つかりません"}
    
    prompt = f"""
    以下の官能小説の選択された部分を、より詳細に拡張してください。
    
    選択されたセクション:
    {selected_section}
    
    拡張係数: {expansion_factor}（現在の長さの{expansion_factor}倍に）
    
    以下の条件に従って拡張してください:
    1. セクションの基本的な内容や流れは維持する
    2. 描写をより詳細にし、感情や感覚、心理描写を追加する
    3. キャラクターの内面や反応をより深く掘り下げる
    4. セクションの始まりと終わりは変更せず、中間部分を拡張する
    5. 文体やトーンとの一貫性を保つ
    6. 村上龍のようなハードボイルドで都会的な表現を使用する
    7. 数値的な身体描写は避け、文学的表現を用いる
    
    拡張されたセクションのみを返してください。
    """
    
    # API呼び出し
    expanded_section = grok_api.generate_text(prompt, max_tokens=int(len(selected_section) * expansion_factor * 1.2))
    
    # 元の物語に拡張されたセクションを組み込む
    expanded_text = story_text[:start_index] + expanded_section + story_text[end_index:]
    
    # 結果をフォーマット
    expanded_story = dict(story_data)
    expanded_story["text"] = expanded_text
    expanded_story["section_expansion"] = {
        "section_start": section_start[:50] + "..." if len(section_start) > 50 else section_start,
        "section_end": section_end[:50] + "..." if len(section_end) > 50 else section_end,
        "expansion_factor": expansion_factor
    }
    
    # 拡張された物語の保存
    expanded_id = str(uuid.uuid4())
    story_service.save_story(expanded_id, expanded_story)
    
    return {
        "id": expanded_id,
        "chapter": expanded_story.get("chapter", 1),
        "text": expanded_text,
        "expanded_section": expanded_section
    }