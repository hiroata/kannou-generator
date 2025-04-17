import os
import json
import uuid
from api import grok_api
from services import story_service

def adjust_explicitness_level(story_id, level=6):
    """
    物語の露骨さのレベルを調整する
    
    Args:
        story_id (str): 物語ID
        level (int): 露骨さのレベル（1: 最も控えめ、6: 極端に露骨、デフォルトは6）
        
    Returns:
        dict: 調整された物語
    """
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    story_text = story_data.get("text", "")
    style = story_data.get("style", "murakami")
    
    level_descriptions = {
        1: "非常に控えめで暗示的。性的な内容は間接的に示唆され、比喩や象徴が多用される。具体的な性的行為や性器の描写はほぼ無し。",
        2: "控えめだが暗示的。性的な内容は主に暗示され、直接的な表現は少ない。性的行為は婉曲的に描写され、性器の具体的な描写は避ける。",
        3: "バランスの取れた表現。性的な内容は比較的直接的に描写されるが、過度に露骨ではない。性的行為や性器への言及はあるが、表現は慎重に選ばれる。",
        4: "露骨で直接的。性的内容は遠慮なく描写され、性的行為や性器の詳細な描写を含む。卑猥な言葉や淫語が使用されるが、過度な繰り返しは避ける。",
        5: "非常に露骨で赤裸々。性的内容は最大限に詳細かつ直接的に描写され、性的行為や性器の徹底的な描写を含む。卑猥な言葉や淫語が頻繁に使用される。",
        6: "極端に露骨で異常。性的内容を異常なまでに詳細かつ過激に描写し、卑猥な言葉や淫語を極限まで多用。読者の興奮を極端に煽る表現を追求。"
    }
    
    level_desc = level_descriptions.get(level, level_descriptions[6])
    
    prompt = f"""
    以下の官能小説の露骨さのレベルを調整してください。
    
    物語の内容: {story_text}
    目標の露骨さレベル: {level}（{level_desc}）
    
    条件:
    1. 物語の基本的な内容と展開は維持
    2. 性的表現を指定された露骨さレベルに調整
    3. 文体は「{style}」スタイルを維持
    4. キャラクターの一貫性を保つ
    5. 村上龍風のハードボイルドな文体を維持
    6. 過激で卑猥な表現を多用し、読者の興奮を極限まで高める
    
    調整された物語を生成してください。
    """
    
    adjusted_text = grok_api.generate_text(prompt, max_tokens=len(story_text) * 1.2, temperature=0.9)
    
    adjusted_story = dict(story_data)
    adjusted_story["text"] = adjusted_text
    adjusted_story["explicitness_level"] = level
    
    adjusted_id = str(uuid.uuid4())
    story_service.save_story(adjusted_id, adjusted_story)
    
    return {
        "id": adjusted_id,
        "chapter": adjusted_story.get("chapter", 1),
        "text": adjusted_text,
        "explicitness_level": level
    }

def analyze_explicitness(story_text):
    """
    物語の露骨さを分析する
    
    Args:
        story_text (str): 物語のテキスト
        
    Returns:
        dict: 分析結果
    """
    sexual_words_explicit = ["オマンコ", "マンコ", "チンポ", "ちんぽ", "勃起", "射精", "イク", "潮", "精液", "挿入", 
                             "肉棒", "膣内", "陰茎", "陰唇", "潮吹き", "連続絶頂", "性奴隷"]
    sexual_expressions = ["あぁん", "んっ", "いやぁ", "ふぁん", "もっと", "激しく", "奥", "気持ちいい", "イク", "イッ"]
    
    counts = {
        "explicit": sum(story_text.count(word) for word in sexual_words_explicit),
        "expressions": sum(story_text.count(expr) for expr in sexual_expressions)
    }
    
    total_chars = len(story_text)
    explicitness_score = min(6, (
        (counts["explicit"] * 3 + counts["expressions"] * 2) / total_chars * 1000
    )) if total_chars > 0 else 0
    
    explicitness_level = round(explicitness_score)
    if explicitness_level < 1:
        explicitness_level = 1
    elif explicitness_level > 6:
        explicitness_level = 6
    
    level_descriptions = {
        1: "非常に控えめで暗示的",
        2: "控えめだが暗示的",
        3: "バランスの取れた表現",
        4: "露骨で直接的",
        5: "非常に露骨で赤裸々",
        6: "極端に露骨で異常"
    }
    
    return {
        "explicitness_level": explicitness_level,
        "explicitness_description": level_descriptions.get(explicitness_level, "不明"),
        "explicitness_score": round(explicitness_score, 2),
        "total_chars": total_chars
    }

def adjust_specific_scene(story_id, scene_start, scene_end, target_level):
    """
    物語の特定のシーンの露骨さを調整する
    
    Args:
        story_id (str): 物語ID
        scene_start (str): シーンの開始部分
        scene_end (str): シーンの終了部分
        target_level (int): 目標の露骨さレベル（1-6）
        
    Returns:
        dict: 調整された物語
    """
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    story_text = story_data.get("text", "")
    
    try:
        start_index = story_text.index(scene_start)
        end_index = story_text.index(scene_end, start_index) + len(scene_end)
        scene_text = story_text[start_index:end_index]
    except ValueError:
        return {"error": "指定されたシーンが見つかりません"}
    
    level_descriptions = {
        1: "非常に控えめで暗示的。性的な内容は間接的に示唆され、比喩や象徴が多用される。",
        2: "控えめだが暗示的。性的な内容は主に暗示され、直接的な表現は少ない。",
        3: "バランスの取れた表現。性的な内容は比較的直接的に描写されるが、過度に露骨ではない。",
        4: "露骨で直接的。性的内容は遠慮なく描写され、性的行為や性器の詳細な描写を含む。",
        5: "非常に露骨で赤裸々。性的内容は最大限に詳細かつ直接的に描写される。",
        6: "極端に露骨で異常。性的内容を異常なまでに詳細かつ過激に描写し、読者の興奮を極端に煽る。"
    }
    
    level_desc = level_descriptions.get(target_level, level_descriptions[6])
    
    prompt = f"""
    以下の官能小説のシーンを、目標の露骨さレベルに調整してください。
    
    シーンのテキスト: {scene_text}
    目標の露骨さレベル: {target_level}（{level_desc}）
    
    条件:
    1. シーンの基本的な内容と展開は維持
    2. 性的表現を指定された露骨さレベルに調整
    3. 文体やトーンを維持
    4. 前後の文脈との一貫性を保つ
    5. 村上龍風のハードボイルドな描写を維持
    6. 過激で卑猥な表現を多用し、読者の興奮を極限まで高める
    
    調整されたシーンのテキストを返してください。
    """
    
    adjusted_scene = grok_api.generate_text(prompt, max_tokens=len(scene_text) * 1.2, temperature=0.9)
    
    adjusted_text = story_text[:start_index] + adjusted_scene + story_text[end_index:]
    
    adjusted_story = dict(story_data)
    adjusted_story["text"] = adjusted_text
    adjusted_story["scene_adjustment"] = {
        "scene_start": scene_start[:50] + "..." if len(scene_start) > 50 else scene_start,
        "scene_end": scene_end[:50] + "..." if len(scene_end) > 50 else scene_end,
        "target_level": target_level
    }
    
    adjusted_id = str(uuid.uuid4())
    story_service.save_story(adjusted_id, adjusted_story)
    
    return {
        "id": adjusted_id,
        "chapter": adjusted_story.get("chapter", 1),
        "text": adjusted_text,
        "adjusted_scene": adjusted_scene
    }