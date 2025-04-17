import os
import json
import uuid
from api import grok_api
from services import story_service

def adjust_explicitness_level(story_id, level=3):
    """
    物語の露骨さのレベルを調整する
    
    Args:
        story_id (str): 物語ID
        level (int): 露骨さのレベル（1: 最も控えめ、5: 最も露骨）
        
    Returns:
        dict: 調整された物語
    """
    # 物語データを取得
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    # 物語のテキスト
    story_text = story_data.get("text", "")
    
    # 文体を取得
    style = story_data.get("style", "murakami")
    
    # 露骨さレベルの説明
    level_descriptions = {
        1: "非常に控えめで暗示的。性的な内容は間接的に示唆され、比喩や象徴が多用される。具体的な性的行為や性器の描写はほぼ無し。",
        2: "控えめだが暗示的。性的な内容は主に暗示され、直接的な表現は少ない。性的行為は婉曲的に描写され、性器の具体的な描写は避ける。",
        3: "バランスの取れた表現。性的な内容は比較的直接的に描写されるが、過度に露骨ではない。性的行為や性器への言及はあるが、表現は慎重に選ばれる。",
        4: "露骨で直接的。性的内容は遠慮なく描写され、性的行為や性器の詳細な描写を含む。卑猥な言葉や淫語が使用されるが、過度な繰り返しは避ける。",
        5: "非常に露骨で赤裸々。性的内容は最大限に詳細かつ直接的に描写され、性的行為や性器の徹底的な描写を含む。卑猥な言葉や淫語が頻繁に使用される。"
    }
    
    level_desc = level_descriptions.get(level, level_descriptions[3])
    
    prompt = f"""
    以下の官能小説の露骨さのレベルを調整してください。
    
    物語の内容:
    {story_text}
    
    目標の露骨さレベル: {level}
    説明: {level_desc}
    
    以下の条件に従って調整してください:
    1. 物語の基本的な内容や展開は維持する
    2. 指定された露骨さレベルに合わせて性的表現を調整する
    3. 文体全体は「{style}」スタイルを維持する
    4. キャラクターの一貫性を保つ
    5. ハードボイルドな村上龍風の文体を用いる

    主な調整ポイント:
    - 性的行為の描写の詳細度
    - 性器や体の部位への言及の直接性
    - 卑猥な言葉や淫語の使用頻度
    - 性的感覚や反応の描写の詳細度
    - 罪悪感や羞恥心の強調度
    
    レベル{level}の露骨さに調整された物語を生成してください。
    """
    
    # API呼び出し
    adjusted_text = grok_api.generate_text(prompt, max_tokens=len(story_text) * 1.2)
    
    # 結果をフォーマット
    adjusted_story = dict(story_data)
    adjusted_story["text"] = adjusted_text
    adjusted_story["explicitness_level"] = level
    
    # 調整された物語の保存
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
    # 性的単語のリスト（日本語）
    sexual_words_basic = ["性", "エロ", "セックス", "愛撫", "キス", "抱き合", "抱擁"]
    sexual_words_medium = ["胸", "乳", "股間", "下半身", "裸", "全裸", "下着", "唇", "舌", "舐"]
    sexual_words_explicit = ["オマンコ", "マンコ", "チンポ", "ちんぽ", "勃起", "射精", "イク", "潮", "精液", "挿入"]
    
    # 淫語のリスト
    sexual_expressions = ["あぁん", "んっ", "いやぁ", "ふぁん", "もっと", "激しく", "奥", "気持ちいい", "イク", "イッ"]
    
    # 単語の出現回数をカウント
    counts = {
        "basic": sum(story_text.count(word) for word in sexual_words_basic),
        "medium": sum(story_text.count(word) for word in sexual_words_medium),
        "explicit": sum(story_text.count(word) for word in sexual_words_explicit),
        "expressions": sum(story_text.count(expr) for expr in sexual_expressions)
    }
    
    # 総文字数
    total_chars = len(story_text)
    
    # 性的単語の割合
    sexual_word_ratio = (counts["basic"] + counts["medium"] + counts["explicit"]) / total_chars if total_chars > 0 else 0
    
    # 露骨さスコアの計算（0-5のスケール）
    explicitness_score = min(5, (
        (counts["basic"] * 0.5 + counts["medium"] * 1.5 + counts["explicit"] * 3 + counts["expressions"] * 2)
        / total_chars * 1000
    )) if total_chars > 0 else 0
    
    # スコアを丸めて整数のレベルに変換
    explicitness_level = round(explicitness_score)
    if explicitness_level < 1:
        explicitness_level = 1
    elif explicitness_level > 5:
        explicitness_level = 5
    
    # レベルの説明
    level_descriptions = {
        1: "非常に控えめで暗示的",
        2: "控えめだが暗示的",
        3: "バランスの取れた表現",
        4: "露骨で直接的",
        5: "非常に露骨で赤裸々"
    }
    
    # 分析結果をまとめる
    analysis = {
        "explicitness_level": explicitness_level,
        "explicitness_description": level_descriptions.get(explicitness_level, "不明"),
        "explicitness_score": round(explicitness_score, 2),
        "word_counts": counts,
        "sexual_word_ratio": round(sexual_word_ratio * 100, 2),
        "total_chars": total_chars
    }
    
    return analysis

def adjust_specific_scene(story_id, scene_start, scene_end, target_level):
    """
    物語の特定のシーンの露骨さを調整する
    
    Args:
        story_id (str): 物語ID
        scene_start (str): シーンの開始部分
        scene_end (str): シーンの終了部分
        target_level (int): 目標の露骨さレベル（1-5）
        
    Returns:
        dict: 調整された物語
    """
    # 物語データを取得
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    # 物語のテキスト
    story_text = story_data.get("text", "")
    
    # シーンの抽出
    try:
        start_index = story_text.index(scene_start)
        end_index = story_text.index(scene_end, start_index) + len(scene_end)
        scene_text = story_text[start_index:end_index]
    except ValueError:
        return {"error": "指定されたシーンが見つかりません"}
    
    # 露骨さレベルの説明
    level_descriptions = {
        1: "非常に控えめで暗示的。性的な内容は間接的に示唆され、比喩や象徴が多用される。",
        2: "控えめだが暗示的。性的な内容は主に暗示され、直接的な表現は少ない。",
        3: "バランスの取れた表現。性的な内容は比較的直接的に描写されるが、過度に露骨ではない。",
        4: "露骨で直接的。性的内容は遠慮なく描写され、性的行為や性器の詳細な描写を含む。",
        5: "非常に露骨で赤裸々。性的内容は最大限に詳細かつ直接的に描写される。"
    }
    
    level_desc = level_descriptions.get(target_level, level_descriptions[3])
    
    prompt = f"""
    以下の官能小説の一部分の露骨さのレベルを調整してください。
    
    シーンのテキスト:
    {scene_text}
    
    目標の露骨さレベル: {target_level}
    説明: {level_desc}
    
    以下の条件に従って調整してください:
    1. シーンの基本的な内容や展開は維持する
    2. 指定された露骨さレベルに合わせて性的表現を調整する
    3. 文体や全体のトーンを維持する
    4. 前後の文脈との一貫性を保つ
    5. 村上龍風のハードボイルドな描写を維持する
    
    調整されたシーンのテキストのみを返してください。
    """
    
    # API呼び出し
    adjusted_scene = grok_api.generate_text(prompt, max_tokens=len(scene_text) * 1.2)
    
    # 元の物語に調整されたシーンを組み込む
    adjusted_text = story_text[:start_index] + adjusted_scene + story_text[end_index:]
    
    # 結果をフォーマット
    adjusted_story = dict(story_data)
    adjusted_story["text"] = adjusted_text
    adjusted_story["scene_adjustment"] = {
        "scene_start": scene_start[:50] + "..." if len(scene_start) > 50 else scene_start,
        "scene_end": scene_end[:50] + "..." if len(scene_end) > 50 else scene_end,
        "target_level": target_level
    }
    
    # 調整された物語の保存
    adjusted_id = str(uuid.uuid4())
    story_service.save_story(adjusted_id, adjusted_story)
    
    return {
        "id": adjusted_id,
        "chapter": adjusted_story.get("chapter", 1),
        "text": adjusted_text,
        "adjusted_scene": adjusted_scene
    }