# -*- coding: utf-8 -*- # 日本語コメントのため
from flask import Flask, render_template, request, redirect, url_for, session, flash
from markupsafe import Markup
import os
import importlib
from services import setting_service, synopsis_service, story_service, enhancement_service, dialog_service
from config import AVAILABLE_MODELS

app = Flask(__name__)
app.secret_key = os.urandom(24)

# nl2brフィルター追加（改行をHTMLのbrタグに変換する）
@app.template_filter('nl2br')
def nl2br_filter(text):
    if not text:
        return ""
    return Markup(str(text).replace('\n', '<br>'))

@app.route('/')
def index():
    """トップページ"""
    return render_template('index.html', available_models=AVAILABLE_MODELS)

@app.route('/custom_setting', methods=['POST'])
def custom_setting():
    """カスタム設定からの生成処理"""
    custom_scenario = request.form.get('custom_scenario', '')
    style = request.form.get('style', 'murakami')  # スタイルの取得
    model = request.form.get('model', 'grok')  # モデル選択
    
    result = setting_service.generate_setting_from_scenario(
        model=model,
        scenario=custom_scenario
    )
    if "error" in result.get("setting", {}):
        flash(f"設定の生成中にエラーが発生しました: {result['setting'].get('error', '不明なエラー')}")
        return redirect(url_for('index'))
    session['setting_id'] = result['id']
    session['style'] = style  # セッションにスタイルを保存
    session['model'] = model  # セッションにモデルを保存
    return redirect(url_for('synopsis_direct'))

@app.route('/setting', methods=['GET', 'POST'])
def setting():
    """設定ジェネレーターページ"""
    if request.method == 'POST':
        setting_type = request.form.get('setting_type', '一般')
        additional_details = request.form.get('additional_details', '')
        style = request.form.get('style', 'murakami')  # スタイルの取得
        model = request.form.get('model', 'grok')  # モデル選択
        
        result = setting_service.generate_setting(
            model=model,
            setting_type=setting_type,
            additional_details=additional_details
        )
        if "error" in result.get("setting", {}):
            flash(f"設定の生成中にエラーが発生しました: {result['setting'].get('error', '不明なエラー')}")
            return render_template('setting.html', available_models=AVAILABLE_MODELS)
        session['setting_id'] = result['id']
        session['style'] = style  # セッションにスタイルを保存
        session['model'] = model  # セッションにモデルを保存
        return redirect(url_for('synopsis'))
    return render_template('setting.html', available_models=AVAILABLE_MODELS)

@app.route('/synopsis_direct', methods=['GET'])
def synopsis_direct():
    """設定から直接あらすじと1話目を生成"""
    setting_id = session.get('setting_id')
    if not setting_id:
        flash("設定が見つかりません。最初からやり直してください。")
        return redirect(url_for('index'))
    setting_data = setting_service.load_setting(setting_id)
    if not setting_data:
        flash(f"設定データ(ID: {setting_id})の読み込みに失敗しました。")
        return redirect(url_for('index'))
    
    # スタイルとモデルをセッションから取得
    style = session.get('style', 'murakami')
    model = session.get('model', 'grok')
    
    synopsis_result = synopsis_service.generate_synopses(
        setting_id,
        model=model,
        style=style,
        num_synopses=1
    )
    synopses = synopsis_result.get('synopses', [])
    if "error" in synopsis_result or not synopses:
        flash(f"あらすじの生成中にエラーが発生しました: {synopsis_result.get('error', '不明なエラー')}")
        return render_template('synopsis.html', setting=setting_data, available_models=AVAILABLE_MODELS)
    session['synopsis_id'] = synopsis_result['id']
    story_result = story_service.generate_story(
        synopsis_result['id'], 0,
        model=model,
        style=style,
        chapter=1
    )
    if "error" in story_result:
        flash(f"第1話の生成中にエラーが発生しました: {story_result.get('error', '不明なエラー')}")
        return render_template('synopsis.html', synopses=synopses, setting=setting_data, available_models=AVAILABLE_MODELS)
    return render_template('story.html', story=story_result, synopsis_index=0, style=style, model=model, available_models=AVAILABLE_MODELS)

@app.route('/synopsis', methods=['GET', 'POST'])
def synopsis():
    """あらすじページ"""
    setting_id = session.get('setting_id')
    if not setting_id:
        flash("設定が見つかりません。最初からやり直してください。")
        return redirect(url_for('setting'))
    setting_data = setting_service.load_setting(setting_id)
    if not setting_data:
        flash(f"設定データ(ID: {setting_id})の読み込みに失敗しました。")
        return redirect(url_for('setting'))
    if request.method == 'POST':
        style = request.form.get('style', 'murakami')
        model = request.form.get('model', 'grok')  # モデル選択
        session['style'] = style  # セッションにスタイルを保存
        session['model'] = model  # セッションにモデルを保存
        
        result = synopsis_service.generate_synopses(
            setting_id,
            model=model,
            style=style,
            num_synopses=1
        )
        synopses = result.get('synopses', [])
        if "error" in result or not synopses:
            flash(f"あらすじの生成中にエラーが発生しました: {result.get('error', '不明なエラー')}")
            return render_template('synopsis.html', setting=setting_data, available_models=AVAILABLE_MODELS)
        session['synopsis_id'] = result['id']
        return render_template('synopsis.html', synopses=synopses, setting=setting_data, style=style, model=model, available_models=AVAILABLE_MODELS)
    return render_template('synopsis.html', setting=setting_data, style=session.get('style', 'murakami'), model=session.get('model', 'grok'), available_models=AVAILABLE_MODELS)

@app.route('/story', methods=['GET', 'POST'])
def story():
    """小説ページ"""
    synopsis_id = session.get('synopsis_id')
    if not synopsis_id:
        flash("あらすじ情報が見つかりません。あらすじを生成または選択してください。")
        return redirect(url_for('synopsis') if session.get('setting_id') else url_for('setting'))
    synopsis_data = synopsis_service.load_synopsis(synopsis_id)
    if not synopsis_data or 'synopses' not in synopsis_data or not synopsis_data['synopses']:
        flash(f"あらすじデータ(ID: {synopsis_id})の読み込みに失敗したか、内容が空です。")
        return redirect(url_for('synopsis') if session.get('setting_id') else url_for('setting'))
    if request.method == 'POST':
        style = request.form.get('style', 'murakami')
        model = request.form.get('model', 'grok')  # モデル選択
        session['style'] = style  # セッションにスタイルを保存
        session['model'] = model  # セッションにモデルを保存
        
        synopsis_index = int(request.form.get('synopsis_index', 0))
        chapter = int(request.form.get('chapter', 1))
        next_chapter_direction = request.form.get('next_chapter_direction', '')
        explicitness_level = int(request.form.get('explicitness_level', 6))  # 卑猥さ強調のためデフォルトを高めに
        
        # 強化オプションの取得（チェックされていないと None を返すので False に変換）
        enhance_psychology = request.form.get('enhance_psychology') is not None
        enhance_emotions = request.form.get('enhance_emotions') is not None
        enhance_sensory = request.form.get('enhance_sensory') is not None
        enhance_voice = request.form.get('enhance_voice') is not None
        add_psychological_themes = request.form.get('add_psychological_themes') is not None
        
        enhance_options = {
            "explicitness_level": explicitness_level,
            "enhance_psychology": enhance_psychology,
            "enhance_emotions": enhance_emotions,
            "enhance_sensory": enhance_sensory,
            "enhance_voice": enhance_voice,
            "add_psychological_themes": add_psychological_themes
        }
        
        if next_chapter_direction:
            # 卑猥な長文セリフと文学性を両立する指示を追加
            literary_directive = (
                "\n【重要】卑猥な淫語セリフを長文で生成し、過激で興奮を誘う表現を強調してください。"
                f"ただし、{style}のような文学的文体を維持し、直接的な数値表現（年齢やバストサイズなど）は避け、"
                "比喩と描写で読者の想像力を刺激してください。"
            )
            next_chapter_direction += literary_directive
        
        result = story_service.generate_story(
            synopsis_id, synopsis_index,
            model=model,
            style=style,
            chapter=chapter,
            direction=next_chapter_direction,
            enhance_options=enhance_options
        )
        
        if "error" in result:
            flash(f"小説の生成中にエラーが発生しました: {result.get('error', '不明なエラー')}")
            return render_template('story.html', synopses=synopsis_data.get('synopses'), setting_id=synopsis_data.get('setting_id'), synopsis_index=synopsis_index, style=style, model=model, available_models=AVAILABLE_MODELS)
        
        # 強化オプションがONの場合は強化処理
        if any([enhance_psychology, enhance_emotions, enhance_sensory, enhance_voice, add_psychological_themes]):
            enhanced_result = enhancement_service.enhance_story(result["id"], enhance_options)
            if "error" not in enhanced_result:
                result = enhanced_result
        
        return render_template('story.html', story=result, synopsis_index=synopsis_index, style=style, model=model, enhanced=True, available_models=AVAILABLE_MODELS)
    
    return render_template('story.html', synopses=synopsis_data.get('synopses'), setting_id=synopsis_data.get('setting_id'), style=session.get('style', 'murakami'), model=session.get('model', 'grok'), available_models=AVAILABLE_MODELS)

# enhance_dialogルートを追加
@app.route('/enhance_dialog/<story_id>', methods=['GET', 'POST'])
def enhance_dialog(story_id):
    """セリフ強化ページ"""
    from config import EROTIC_DIALOG_PATTERNS, DIALOG_ENHANCEMENT_PRESETS
    
    story_data = story_service.load_story(story_id)
    if not story_data:
        flash("指定された小説が見つかりません。")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        preset = request.form.get('preset', 'extreme')
        intensity = int(request.form.get('intensity', 5))
        pattern_types = request.form.getlist('pattern_types')
        model = request.form.get('model', session.get('model', 'grok'))  # モデル選択
        
        # パターンタイプが選択されていない場合はプリセットから取得
        if not pattern_types and preset in DIALOG_ENHANCEMENT_PRESETS:
            pattern_types = DIALOG_ENHANCEMENT_PRESETS[preset]['patterns']
        
        result = dialog_service.enhance_erotic_dialog(
            story_id=story_id,
            preset=preset,
            custom_patterns=pattern_types,
            custom_intensity=intensity,
            model=model  # モデルパラメータを追加
        )
        
        if "error" in result:
            flash(f"セリフ強化中にエラーが発生しました: {result.get('error', '不明なエラー')}")
            return redirect(url_for('story', story_id=story_id))
        
        return render_template('story.html', story=result, synopsis_index=0, style=story_data.get('style', 'murakami'), model=model, enhanced=True, available_models=AVAILABLE_MODELS)
    
    return render_template('dialog_enhance.html', 
                          story=story_data, 
                          patterns=EROTIC_DIALOG_PATTERNS,
                          presets=DIALOG_ENHANCEMENT_PRESETS,
                          model=session.get('model', 'grok'),
                          available_models=AVAILABLE_MODELS)

if __name__ == '__main__':
    os.makedirs('data/settings', exist_ok=True)
    os.makedirs('data/synopses', exist_ok=True)
    os.makedirs('data/stories', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)