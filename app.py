# -*- coding: utf-8 -*- # 日本語コメントのため
from flask import Flask, render_template, request, redirect, url_for, session, flash
from markupsafe import Markup
import os
from services import setting_service, synopsis_service, story_service, enhancement_service, dialog_service
from api import grok_api  # Grok 3専用のAPIモジュール

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
    return render_template('index.html')

@app.route('/custom_setting', methods=['POST'])
def custom_setting():
    """カスタム設定からの生成処理"""
    custom_scenario = request.form.get('custom_scenario', '')
    result = setting_service.generate_setting_from_scenario(
        model="grok",  # Grok 3に固定
        scenario=custom_scenario
    )
    if "error" in result.get("setting", {}):
        flash(f"設定の生成中にエラーが発生しました: {result['setting'].get('error', '不明なエラー')}")
        return redirect(url_for('index'))
    session['setting_id'] = result['id']
    return redirect(url_for('synopsis_direct'))

@app.route('/setting', methods=['GET', 'POST'])
def setting():
    """設定ジェネレーターページ"""
    if request.method == 'POST':
        setting_type = request.form.get('setting_type', '一般')
        additional_details = request.form.get('additional_details', '')
        result = setting_service.generate_setting(
            model="grok",  # Grok 3に固定
            setting_type=setting_type,
            additional_details=additional_details
        )
        if "error" in result.get("setting", {}):
            flash(f"設定の生成中にエラーが発生しました: {result['setting'].get('error', '不明なエラー')}")
            return render_template('setting.html')
        session['setting_id'] = result['id']
        return redirect(url_for('synopsis'))
    return render_template('setting.html')

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
    synopsis_result = synopsis_service.generate_synopses(
        setting_id,
        model="grok",  # Grok 3に固定
        style="murakami",
        num_synopses=1
    )
    synopses = synopsis_result.get('synopses', [])
    if "error" in synopsis_result or not synopses:
        flash(f"あらすじの生成中にエラーが発生しました: {synopsis_result.get('error', '不明なエラー')}")
        return render_template('synopsis.html', setting=setting_data)
    session['synopsis_id'] = synopsis_result['id']
    story_result = story_service.generate_story(
        synopsis_result['id'], 0,
        model="grok",  # Grok 3に固定
        style="murakami",
        chapter=1
    )
    if "error" in story_result:
        flash(f"第1話の生成中にエラーが発生しました: {story_result.get('error', '不明なエラー')}")
        return render_template('synopsis.html', synopses=synopses, setting=setting_data)
    return render_template('story.html', story=story_result, synopsis_index=0, style="murakami")

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
        result = synopsis_service.generate_synopses(
            setting_id,
            model="grok",  # Grok 3に固定
            style=style,
            num_synopses=1
        )
        synopses = result.get('synopses', [])
        if "error" in result or not synopses:
            flash(f"あらすじの生成中にエラーが発生しました: {result.get('error', '不明なエラー')}")
            return render_template('synopsis.html', setting=setting_data)
        session['synopsis_id'] = result['id']
        return render_template('synopsis.html', synopses=synopses, setting=setting_data)
    return render_template('synopsis.html', setting=setting_data)

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
        synopsis_index = int(request.form.get('synopsis_index', 0))
        chapter = int(request.form.get('chapter', 1))
        next_chapter_direction = request.form.get('next_chapter_direction', '')
        explicitness_level = int(request.form.get('explicitness_level', 6))  # 卑猥さ強調のためデフォルトを高めに
        enhance_options = {
            "explicitness_level": explicitness_level
        }
        if next_chapter_direction:
            # 卑猥な長文セリフと文学性を両立する指示を追加
            literary_directive = (
                "\n【重要】卑猥な淫語セリフを長文で生成し、過激で興奮を誘う表現を強調してください。"
                "ただし、村上龍のような文学的文体を維持し、直接的な数値表現（年齢やバストサイズなど）は避け、"
                "比喩と描写で読者の想像力を刺激してください。"
            )
            next_chapter_direction += literary_directive
        result = story_service.generate_story(
            synopsis_id, synopsis_index,
            model="grok",  # Grok 3に固定
            style=style,
            chapter=chapter,
            direction=next_chapter_direction,
            enhance_options=enhance_options
        )
        if "error" in result:
            flash(f"小説の生成中にエラーが発生しました: {result.get('error', '不明なエラー')}")
            return render_template('story.html', synopses=synopsis_data.get('synopses'), setting_id=synopsis_data.get('setting_id'), synopsis_index=synopsis_index, style=style)
        return render_template('story.html', story=result, synopsis_index=synopsis_index, style=style, enhanced=True)
    return render_template('story.html', synopses=synopsis_data.get('synopses'), setting_id=synopsis_data.get('setting_id'))

# enhance_dialogルートを追加
@app.route('/enhance_dialog/<story_id>', methods=['GET', 'POST'])
def enhance_dialog(story_id):
    """セリフ強化ページ"""
    # ここにセリフ強化のロジックを後で実装できます
    return f"Story ID: {story_id} のセリフを強化します"  # 仮のレスポンス

if __name__ == '__main__':
    os.makedirs('data/settings', exist_ok=True)
    os.makedirs('data/synopses', exist_ok=True)
    os.makedirs('data/stories', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)