import os
import json
import uuid
import re
from api import grok_api
from services import story_service
from config import EROTIC_DIALOG_PATTERNS, SENSORY_EXPRESSIONS, DIALOG_ENHANCEMENT_PRESETS

def adjust_dialog_narrative_balance(story_id, dialog_ratio=50, dialog_style="extreme"):
    """
    小説のセリフと地の文のバランスを調整する
    
    Args:
        story_id (str): 物語ID
        dialog_ratio (int): セリフの比率（0-100%）
        dialog_style (str): セリフのスタイル ('extreme'がデフォルト)
    
    Returns:
        dict: 調整された物語
    """
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    story_text = story_data.get("text", "")
    style = story_data.get("style", "murakami")
    
    dialog_style_descriptions = {
        "explicit": "露骨で直接的な表現を使用したセリフ。性的な欲望や行為を遠慮なく言語化する。",
        "metaphorical": "比喩や暗示を多用した間接的なセリフ。直接的な表現を避けつつも、性的なニュアンスを伝える。",
        "internal": "内的独白や思考を多く含むセリフ。キャラクターの内面の葛藤や欲望を言語化する。",
        "emotional": "感情表現が豊かなセリフ。喜び、興奮、恐れ、羞恥などの感情を強調する。",
        "extreme": "極端に露骨で卑猥な表現を使用し、読者の興奮を極限まで煽る。淫語やオノマトペを多用。"
    }
    
    dialog_style_desc = dialog_style_descriptions.get(dialog_style, dialog_style_descriptions["extreme"])
    
    prompt = f"""
    以下の官能小説のセリフと地の文のバランスを調整してください。
    
    物語の内容: {story_text}
    調整パラメータ:
    - セリフの比率: 全体の約{dialog_ratio}%
    - セリフのスタイル: {dialog_style}（{dialog_style_desc}）
    
    条件:
    1. 物語の基本的な内容と展開は維持
    2. セリフと地の文の比率を指定された割合に近づける
    3. セリフは指定されたスタイルを反映し、卑猥で長文の淫語セリフを多用
    4. 文体は「{style}」スタイルを維持し、村上龍のようなハードボイルドな語りで文学的クオリティを保つ
    5. キャラクターの一貫性を維持
    6. 数値的な身体描写は避け、感覚的・文学的表現を用いる
    7. 読者の興奮を極限まで高める過激な表現（オノマトペ「ズチュッ」「グチョッ」、淫語「チンポ」「マンコ」）を積極的に使用
    
    調整された物語を生成してください。
    """
    
    adjusted_text = grok_api.generate_text(prompt, max_tokens=len(story_text) * 1.2, temperature=0.9)
    
    adjusted_story = dict(story_data)
    adjusted_story["text"] = adjusted_text
    adjusted_story["dialog_adjustments"] = {
        "dialog_ratio": dialog_ratio,
        "dialog_style": dialog_style
    }
    
    adjusted_id = str(uuid.uuid4())
    story_service.save_story(adjusted_id, adjusted_story)
    
    return {
        "id": adjusted_id,
        "chapter": adjusted_story.get("chapter", 1),
        "text": adjusted_text,
        "dialog_ratio": dialog_ratio,
        "dialog_style": dialog_style
    }

def extract_dialog(story_text):
    """
    物語からセリフを抽出する
    
    Args:
        story_text (str): 物語のテキスト
        
    Returns:
        list: 抽出されたセリフのリスト
    """
    jp_dialog_pattern = r'「([^」]*)」'
    western_dialog_pattern = r'"([^"]*)"'
    conversation_pattern = r'"([^"]*)"(?:\s*,\s*|\s+)(?:he|she|they|[A-Z][a-z]+)\s+(?:said|replied|asked|whispered|moaned|gasped)'
    
    jp_dialogs = re.findall(jp_dialog_pattern, story_text)
    western_dialogs = re.findall(western_dialog_pattern, story_text)
    conversation_dialogs = re.findall(conversation_pattern, story_text)
    
    return jp_dialogs + western_dialogs + conversation_dialogs

def analyze_dialog_narrative_ratio(story_text):
    """
    物語のセリフと地の文の比率を分析する
    
    Args:
        story_text (str): 物語のテキスト
        
    Returns:
        dict: 分析結果
    """
    dialogs = extract_dialog(story_text)
    dialog_char_count = sum(len(dialog) for dialog in dialogs)
    total_char_count = len(story_text)
    dialog_ratio = round((dialog_char_count / total_char_count) * 100, 2) if total_char_count > 0 else 0
    dialog_count = len(dialogs)
    avg_dialog_length = round(dialog_char_count / dialog_count, 2) if dialog_count > 0 else 0
    
    return {
        "dialog_count": dialog_count,
        "dialog_char_count": dialog_char_count,
        "total_char_count": total_char_count,
        "dialog_ratio": dialog_ratio,
        "avg_dialog_length": avg_dialog_length,
        "dialogs_sample": dialogs[:5] if len(dialogs) > 5 else dialogs
    }

def transform_dialog_style(story_id, target_style="extreme"):
    """
    物語のセリフのスタイルを変換する
    
    Args:
        story_id (str): 物語ID
        target_style (str): 目標のセリフスタイル ('extreme'がデフォルト)
            
    Returns:
        dict: 変換された物語
    """
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    story_text = story_data.get("text", "")
    
    style_descriptions = {
        "explicit": "露骨で直接的な表現を使用したセリフ。性的な欲望や行為を遠慮なく言語化する。具体的な性器の名称や卑猥な言葉を含む。",
        "metaphorical": "比喩や暗示を多用した間接的なセリフ。直接的な表現を避けつつも、性的なニュアンスを伝える。詩的で象徴的な表現を使用。",
        "internal": "内的独白や思考を多く含むセリフ。キャラクターの内面の葛藤や欲望を言語化する。意識の流れを反映した構造。",
        "emotional": "感情表現が豊かなセリフ。喜び、興奮、恐れ、羞恥などの感情を強調する。感嘆符や省略、破壊的な文法構造を含む。",
        "extreme": "極端に露骨で卑猥な表現を使用し、読者の興奮を極限まで煽る。淫語やオノマトペを多用し、日本のエロ同人マンガ風の表現を取り入れる。"
    }
    
    style_desc = style_descriptions.get(target_style, style_descriptions["extreme"])
    
    prompt = f"""
    以下の官能小説のセリフのスタイルを「{target_style}」スタイルに変換してください。
    
    物語の内容: {story_text}
    目標のセリフスタイル: {target_style}（{style_desc}）
    
    条件:
    1. 地の文はそのまま維持し、セリフ部分のみを変換
    2. 「」や""で囲まれたセリフのみを対象
    3. セリフの基本的な内容や意図を維持しつつ、表現方法を変更
    4. キャラクターの個性や関係性を反映
    5. 物語の流れや展開を損なわない
    6. 卑猥で長文の淫語セリフ（「チンポでマンコを壊してぇ！」など）を積極的に使用
    7. 文学的クオリティを保ち、村上龍風のハードボイルドな語りを維持
    
    変換された物語全体を返してください。
    """
    
    transformed_text = grok_api.generate_text(prompt, max_tokens=len(story_text) * 1.2, temperature=0.9)
    
    transformed_story = dict(story_data)
    transformed_story["text"] = transformed_text
    transformed_story["dialog_transformation"] = {
        "original_style": "unknown",
        "target_style": target_style
    }
    
    transformed_id = str(uuid.uuid4())
    story_service.save_story(transformed_id, transformed_story)
    
    return {
        "id": transformed_id,
        "chapter": transformed_story.get("chapter", 1),
        "text": transformed_text,
        "target_style": target_style
    }

def enhance_erotic_dialog(story_id, preset="extreme", custom_patterns=None, custom_intensity=None):
    """
    物語内の性的なセリフだけを強化する機能
    
    Args:
        story_id (str): 物語ID
        preset (str): 強化プリセット名
        custom_patterns (list, optional): カスタムパターンリスト
        custom_intensity (int, optional): カスタム強度（1-7）
        
    Returns:
        dict: 強化された物語
    """
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    story_text = story_data.get("text", "")
    
    preset_config = DIALOG_ENHANCEMENT_PRESETS.get(preset, DIALOG_ENHANCEMENT_PRESETS["extreme"])
    pattern_types = custom_patterns if custom_patterns else preset_config["patterns"]
    intensity = custom_intensity if custom_intensity is not None else preset_config["intensity"]
    
    patterns = []
    for pattern_type in pattern_types:
        patterns.extend(EROTIC_DIALOG_PATTERNS.get(pattern_type, [])[:2])
    
    sensory_examples = [SENSORY_EXPRESSIONS[sense][0] for sense in SENSORY_EXPRESSIONS]
    
    prompt = f"""
    以下の官能小説の「セリフ部分」のみを、より卑猥で官能的な表現に強化してください。
    地の文は変更せず、「」や""で囲まれたセリフのみを対象にしてください。
    
    強化レベル: {intensity}（1は控えめ、7は極端に露骨）
    表現パターン参考: {patterns[:3]}
    五感表現参考: {sensory_examples[:3]}
    
    条件:
    1. セリフを卑猥で長文にし、リアルで詳細な表現にする
    2. 喘ぎ声（「あぁん」「んっ」）やオノマトペ（「ズチュッ」「グチョッ」）を多用
    3. 淫語（「チンポ」「マンコ」）や快感を直接言語化
    4. キャラクターの性格や関係性を反映した口調を維持
    5. 文学的クオリティを保ち、村上龍風のハードボイルドな語りを損なわない
    6. 読者の興奮を極限まで高める過激な表現を追求
    
    原文: {story_text}
    強化された文章全体を返してください。
    """
    
    enhanced_text = grok_api.generate_text(prompt, max_tokens=len(story_text) * 1.2, temperature=0.9)
    
    enhanced_story = dict(story_data)
    enhanced_story["text"] = enhanced_text
    enhanced_story["dialog_enhancement"] = {
        "preset": preset,
        "pattern_types": pattern_types,
        "intensity": intensity
    }
    
    enhanced_id = str(uuid.uuid4())
    story_service.save_story(enhanced_id, enhanced_story)
    
    return {
        "id": enhanced_id,
        "chapter": enhanced_story.get("chapter", 1),
        "text": enhanced_text,
        "enhancement_info": {
            "type": "dialog_enhancement",
            "preset": preset,
            "intensity": intensity
        }
    }

def analyze_dialog_content(story_text):
    """
    物語のセリフを分析して内容の特性を評価する
    
    Args:
        story_text (str): 物語のテキスト
        
    Returns:
        dict: 分析結果
    """
    dialogs = extract_dialog(story_text)
    if not dialogs:
        return {
            "dialog_count": 0,
            "explicit_level": 0,
            "emotion_level": 0,
            "common_expressions": []
        }
    
    explicit_keywords = ["あ", "ん", "イク", "気持ちいい", "感じる", "挿入", "イッ", "もっと", "激しく", "奥", "チンポ", "マンコ", "ズチュッ", "グチョッ"]
    explicit_count = sum(sum(keyword in dialog for keyword in explicit_keywords) for dialog in dialogs)
    
    emotion_keywords = ["愛してる", "好き", "嬉しい", "悲しい", "苦しい", "怖い", "恥ずかしい", "切ない"]
    emotion_count = sum(sum(keyword in dialog for keyword in emotion_keywords) for dialog in dialogs)
    
    avg_length = sum(len(dialog) for dialog in dialogs) / len(dialogs)
    
    common_phrases = []
    for phrase in ["あぁん", "もっと", "いい", "お願い", "だめ", "すごい", "チンポ", "マンコ", "ズチュッ"]:
        phrase_count = sum(phrase in dialog for dialog in dialogs)
        if phrase_count > 0:
            common_phrases.append({"phrase": phrase, "count": phrase_count})
    
    return {
        "dialog_count": len(dialogs),
        "explicit_level": min(7, int(explicit_count / len(dialogs) * 3)),
        "emotion_level": min(5, int(emotion_count / len(dialogs) * 5)),
        "avg_length": avg_length,
        "common_expressions": sorted(common_phrases, key=lambda x: x["count"], reverse=True)[:5]
    }