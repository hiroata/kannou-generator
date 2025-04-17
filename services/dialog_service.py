import os
import json
import uuid
from api import grok_api
from services import story_service

def adjust_dialog_narrative_balance(story_id, dialog_ratio=50, dialog_style="explicit"):
    """
    小説のセリフと地の文のバランスを調整する
    
    Args:
        story_id (str): 物語ID
        dialog_ratio (int): セリフの比率（0-100%）
        dialog_style (str): セリフのスタイル
            - "explicit": 露骨で直接的
            - "metaphorical": 比喩的で間接的
            - "internal": 内的独白が多い
            - "emotional": 感情表現が豊か
            
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
    
    # セリフスタイルの説明
    dialog_style_descriptions = {
        "explicit": "露骨で直接的な表現を使用したセリフ。性的な欲望や行為を遠慮なく言語化する。",
        "metaphorical": "比喩や暗示を多用した間接的なセリフ。直接的な表現を避けつつも、性的なニュアンスを伝える。",
        "internal": "内的独白や思考を多く含むセリフ。キャラクターの内面の葛藤や欲望を言語化する。",
        "emotional": "感情表現が豊かなセリフ。喜び、興奮、恐れ、羞恥などの感情を強調する。"
    }
    
    dialog_style_desc = dialog_style_descriptions.get(dialog_style, "標準的なセリフスタイル")
    
    prompt = f"""
    以下の官能小説のセリフと地の文のバランスを調整してください。
    
    物語の内容:
    {story_text}
    
    調整パラメータ:
    - セリフの比率: 全体の約{dialog_ratio}%
    - セリフのスタイル: {dialog_style}（{dialog_style_desc}）
    
    以下の条件に従って調整してください:
    1. 物語の基本的な内容と展開は維持する
    2. セリフと地の文の比率を指定された割合に近づける
    3. セリフには指定されたスタイルの特性を持たせる
    4. 文体全体は「{style}」スタイルを維持する
    5. キャラクターの一貫性を保つ
    6. 官能描写の質と深さを損なわない
    7. 数値的な身体の描写ではなく、文学的表現を用いる
    8. 村上龍のようなハードボイルドな文体で描写する
    
    調整された物語を生成してください。
    """
    
    # API呼び出し
    adjusted_text = grok_api.generate_text(prompt, max_tokens=len(story_text) * 1.2)
    
    # 結果をフォーマット
    adjusted_story = dict(story_data)
    adjusted_story["text"] = adjusted_text
    adjusted_story["dialog_adjustments"] = {
        "dialog_ratio": dialog_ratio,
        "dialog_style": dialog_style
    }
    
    # 調整された物語の保存
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
    import re
    
    # 日本語のセリフパターン（「」内のテキスト）
    jp_dialog_pattern = r'「([^」]*)」'
    jp_dialogs = re.findall(jp_dialog_pattern, story_text)
    
    # 西洋式のセリフパターン（""内のテキスト）
    western_dialog_pattern = r'"([^"]*)"'
    western_dialogs = re.findall(western_dialog_pattern, story_text)
    
    # 会話文形式のセリフパターン（例: "text," he said.）
    conversation_pattern = r'"([^"]*)"(?:\s*,\s*|\s+)(?:he|she|they|[A-Z][a-z]+)\s+(?:said|replied|asked|whispered|moaned|gasped)'
    conversation_dialogs = re.findall(conversation_pattern, story_text)
    
    # すべてのセリフを結合
    all_dialogs = jp_dialogs + western_dialogs + conversation_dialogs
    
    return all_dialogs

def analyze_dialog_narrative_ratio(story_text):
    """
    物語のセリフと地の文の比率を分析する
    
    Args:
        story_text (str): 物語のテキスト
        
    Returns:
        dict: 分析結果
    """
    # セリフを抽出
    dialogs = extract_dialog(story_text)
    
    # セリフの合計文字数
    dialog_char_count = sum(len(dialog) for dialog in dialogs)
    
    # 全体の文字数
    total_char_count = len(story_text)
    
    # セリフの比率（%）
    dialog_ratio = round((dialog_char_count / total_char_count) * 100, 2) if total_char_count > 0 else 0
    
    # セリフの数
    dialog_count = len(dialogs)
    
    # 平均セリフ長
    avg_dialog_length = round(dialog_char_count / dialog_count, 2) if dialog_count > 0 else 0
    
    # 分析結果
    analysis = {
        "dialog_count": dialog_count,
        "dialog_char_count": dialog_char_count,
        "total_char_count": total_char_count,
        "dialog_ratio": dialog_ratio,
        "avg_dialog_length": avg_dialog_length,
        "dialogs_sample": dialogs[:5] if len(dialogs) > 5 else dialogs
    }
    
    return analysis

def transform_dialog_style(story_id, target_style="explicit"):
    """
    物語のセリフのスタイルを変換する
    
    Args:
        story_id (str): 物語ID
        target_style (str): 目標のセリフスタイル
            - "explicit": 露骨で直接的
            - "metaphorical": 比喩的で間接的
            - "internal": 内的独白が多い
            - "emotional": 感情表現が豊か
            
    Returns:
        dict: 変換された物語
    """
    # 物語データを取得
    story_data = story_service.load_story(story_id)
    if not story_data:
        return {"error": "指定された物語が見つかりません"}
    
    # 物語のテキスト
    story_text = story_data.get("text", "")
    
    # セリフスタイルの説明
    style_descriptions = {
        "explicit": "露骨で直接的な表現を使用したセリフ。性的な欲望や行為を遠慮なく言語化する。具体的な性器の名称や卑猥な言葉を含む。",
        "metaphorical": "比喩や暗示を多用した間接的なセリフ。直接的な表現を避けつつも、性的なニュアンスを伝える。詩的で象徴的な表現を使用。",
        "internal": "内的独白や思考を多く含むセリフ。キャラクターの内面の葛藤や欲望を言語化する。意識の流れを反映した構造。",
        "emotional": "感情表現が豊かなセリフ。喜び、興奮、恐れ、羞恥などの感情を強調する。感嘆符や省略、破壊的な文法構造を含む。"
    }
    
    style_desc = style_descriptions.get(target_style, "標準的なセリフスタイル")
    
    prompt = f"""
    以下の官能小説のセリフのスタイルを「{target_style}」スタイルに変換してください。
    
    物語の内容:
    {story_text}
    
    目標のセリフスタイル: {target_style}
    説明: {style_desc}
    
    以下の条件に従って変換してください:
    1. 地の文はそのまま維持し、セリフ部分のみを変換する
    2. 「」や ""などのセリフのマーカーで囲まれた部分を変換の対象とする
    3. セリフの基本的な内容や意図は維持しながら、表現方法を変更する
    4. キャラクターの個性や関係性を反映したセリフにする
    5. 物語の流れや展開を損なわないようにする
    
    セリフのスタイルが変換された物語全体を返してください。
    """
    
    # API呼び出し
    transformed_text = grok_api.generate_text(prompt, max_tokens=len(story_text) * 1.2)
    
    # 結果をフォーマット
    transformed_story = dict(story_data)
    transformed_story["text"] = transformed_text
    transformed_story["dialog_transformation"] = {
        "original_style": "unknown",
        "target_style": target_style
    }
    
    # 変換された物語の保存
    transformed_id = str(uuid.uuid4())
    story_service.save_story(transformed_id, transformed_story)
    
    return {
        "id": transformed_id,
        "chapter": transformed_story.get("chapter", 1),
        "text": transformed_text,
        "target_style": target_style
    }