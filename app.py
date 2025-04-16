from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from markupsafe import Markup
import os
import re
from services import setting_service, synopsis_service, story_service, enhancement_service

app = Flask(__name__)
app.secret_key = os.urandom(24)

# nl2brフィルター追加（改行をHTMLのbrタグに変換する）
@app.template_filter('nl2br')
def nl2br_filter(text):
    if not text:
        return ""
    return Markup(text.replace('\n', '<br>'))

@app.route('/')
def index():
    """トップページ"""
    return render_template('index.html')

@app.route('/custom_setting', methods=['POST'])
def custom_setting():
    """カスタム設定からの生成処理"""
    if request.method == 'POST':
        custom_scenario = request.form.get('custom_scenario', '')
        
        # カスタムシナリオをもとに設定を生成
        result = setting_service.generate_setting_from_scenario(
            model="grok", 
            scenario=custom_scenario
        )
        
        # エラーチェック
        if "error" in result.get("setting", {}):
            flash(f"設定の生成中にエラーが発生しました: {result['setting'].get('error')}")
            return redirect(url_for('index'))
            
        # セッションに保存
        session['setting_id'] = result['id']
        
        # あらすじに直接進む
        return redirect(url_for('synopsis_direct'))
    
    return redirect(url_for('index'))

@app.route('/setting', methods=['GET', 'POST'])
def setting():
    """設定ジェネレーターページ"""
    if request.method == 'POST':
        # フォームからデータを取得
        setting_type = request.form.get('setting_type', '一般')
        additional_details = request.form.get('additional_details', '')
        
        # 設定を生成
        result = setting_service.generate_setting(model="grok", setting_type=setting_type, additional_details=additional_details)
        
        # エラーチェック
        if "error" in result.get("setting", {}):
            flash(f"設定の生成中にエラーが発生しました: {result['setting'].get('error')}")
            return render_template('setting.html')
            
        # セッションに保存
        session['setting_id'] = result['id']
        
        # あらすじページにリダイレクト
        return redirect(url_for('synopsis'))
    
    return render_template('setting.html')

@app.route('/synopsis_direct', methods=['GET'])
def synopsis_direct():
    """設定から直接あらすじを生成"""
    setting_id = session.get('setting_id')
    if not setting_id:
        return redirect(url_for('setting'))
    
    # 設定データを取得
    setting_data = setting_service.load_setting(setting_id)
    
    # あらすじを自動生成
    result = synopsis_service.generate_synopses(setting_id, model="grok", style="murakami", num_synopses=1)
    
    # セッションに保存
    session['synopsis_id'] = result['id']
    
    # 結果の処理
    synopses = result.get('synopses', [])
    
    # エラーチェック
    if isinstance(synopses, dict) and "error" in synopses:
        flash(f"あらすじの生成中にエラーが発生しました: {synopses.get('error')}")
        return render_template('synopsis.html', setting=setting_data)
    
    # リストでない場合はリストに変換
    if not isinstance(synopses, list):
        synopses = [synopses]
    
    # あらすじ選択ページを表示
    return render_template(
        'synopsis.html',
        synopses=synopses,
        setting=setting_data,
        auto_generated=True
    )

@app.route('/synopsis', methods=['GET', 'POST'])
def synopsis():
    """あらすじページ"""
    setting_id = session.get('setting_id')
    if not setting_id:
        return redirect(url_for('setting'))
    
    if request.method == 'POST':
        # フォームからデータを取得
        style = request.form.get('style', 'murakami')
        
        # あらすじを生成
        result = synopsis_service.generate_synopses(setting_id, model="grok", style=style, num_synopses=1)
        
        # セッションに保存
        session['synopsis_id'] = result['id']
        
        # 結果の処理
        synopses = result.get('synopses', [])
        
        # エラーチェック
        if isinstance(synopses, dict) and "error" in synopses:
            flash(f"あらすじの生成中にエラーが発生しました: {synopses.get('error')}")
            return render_template('synopsis.html', setting=setting_service.load_setting(setting_id))
            
        # リストでない場合はリストに変換
        if not isinstance(synopses, list):
            synopses = [synopses]
        
        # あらすじ選択ページを表示
        return render_template(
            'synopsis.html',
            synopses=synopses,
            setting=setting_service.load_setting(setting_id)
        )
    
    # 設定データを取得
    setting_data = setting_service.load_setting(setting_id)
    
    return render_template('synopsis.html', setting=setting_data)

@app.route('/story', methods=['GET', 'POST'])
def story():
    """小説ページ"""
    synopsis_id = session.get('synopsis_id')
    if not synopsis_id:
        return redirect(url_for('synopsis'))
    
    if request.method == 'POST':
        # フォームからデータを取得
        style = request.form.get('style', 'murakami')
        synopsis_index = int(request.form.get('synopsis_index', 0))
        chapter = int(request.form.get('chapter', 1))
        next_chapter_direction = request.form.get('next_chapter_direction', '')
        
        # 小説を生成
        result = story_service.generate_story(
            synopsis_id, synopsis_index, model="grok", style=style, chapter=chapter,
            direction=next_chapter_direction
        )
        
        # エラーチェック
        if "error" in result:
            flash(f"小説の生成中にエラーが発生しました: {result.get('error')}")
            synopsis_data = synopsis_service.load_synopsis(synopsis_id)
            return render_template(
                'story.html',
                synopses=synopsis_data.get('synopses'),
                setting_id=synopsis_data.get('setting_id')
            )
        
        # 小説を表示
        return render_template('story.html', 
                              story=result, 
                              synopsis_index=synopsis_index, 
                              style=style)
    
    # あらすじデータを取得
    synopsis_data = synopsis_service.load_synopsis(synopsis_id)
    
    return render_template(
        'story.html',
        synopses=synopsis_data.get('synopses'),
        setting_id=synopsis_data.get('setting_id')
    )

@app.route('/enhance_story', methods=['POST'])
def enhance_story():
    """ストーリーを深化させる"""
    story_id = request.form.get('story_id')
    if not story_id:
        flash("ストーリーIDが指定されていません")
        return redirect(url_for('index'))
    
    # オプションの取得
    options = {
        "enhance_psychology": request.form.get('enhance_psychology') == 'on',
        "enhance_emotions": request.form.get('enhance_emotions') == 'on',
        "enhance_sensory": request.form.get('enhance_sensory') == 'on',
        "enhance_voice": request.form.get('enhance_voice') == 'on',
        "add_psychological_themes": request.form.get('add_psychological_themes') == 'on'
    }
    
    # 少なくとも1つのオプションが選択されているか確認
    if not any(options.values()):
        flash("少なくとも1つの強化オプションを選択してください")
        return redirect(url_for('story'))
    
    # ストーリーの強化を実行
    result = enhancement_service.enhance_story(story_id, options)
    
    # エラーチェック
    if "error" in result:
        flash(f"ストーリーの強化中にエラーが発生しました: {result.get('error')}")
        return redirect(url_for('story'))
    
    # 強化されたストーリーを表示
    story_data = story_service.load_story(story_id)
    synopsis_id = story_data.get('synopsis_id')
    synopsis_index = story_data.get('synopsis_index', 0)
    style = story_data.get('style', 'murakami')
    
    return render_template('story.html', 
                          story=result, 
                          synopsis_index=synopsis_index,
                          style=style,
                          enhanced=True)

@app.route('/generate_scene_prompts', methods=['POST'])
def generate_scene_prompts():
    """シーン用SDプロンプトを生成する"""
    story_id = request.form.get('story_id')
    if not story_id:
        flash("ストーリーIDが指定されていません")
        return redirect(url_for('index'))
    
    # シーン数の取得（デフォルトは3）
    num_scenes = int(request.form.get('num_scenes', 3))
    
    # ストーリーデータを取得
    story_data = story_service.load_story(story_id)
    if not story_data:
        flash("指定されたストーリーが見つかりません")
        return redirect(url_for('index'))
    
    # シーンプロンプトを生成
    story_text = story_data.get('text', '')
    prompts_text = enhancement_service.generate_scene_prompts(story_text, num_scenes)
    
    # プロンプトを保存
    enhancement_service.save_scene_prompts(story_id, prompts_text)
    
    # プロンプト表示ページを表示
    synopsis_index = story_data.get('synopsis_index', 0)
    style = story_data.get('style', 'murakami')
    
    return render_template('scene_prompts.html', 
                          story_id=story_id,
                          prompts_text=prompts_text,
                          synopsis_index=synopsis_index,
                          style=style)

@app.route('/api/settings', methods=['POST'])
def api_generate_setting():
    """設定生成API"""
    data = request.json
    setting_type = data.get('setting_type', '一般')
    additional_details = data.get('additional_details', '')
    
    result = setting_service.generate_setting(model="grok", setting_type=setting_type, additional_details=additional_details)
    return jsonify(result)

@app.route('/api/synopses', methods=['POST'])
def api_generate_synopses():
    """あらすじ生成API"""
    data = request.json
    setting_id = data.get('setting_id')
    style = data.get('style', 'murakami')
    
    if not setting_id:
        return jsonify({"error": "設定IDが必要です"})
    
    result = synopsis_service.generate_synopses(setting_id, model="grok", style=style, num_synopses=1)
    return jsonify(result)

@app.route('/api/stories', methods=['POST'])
def api_generate_story():
    """小説生成API"""
    data = request.json
    synopsis_id = data.get('synopsis_id')
    synopsis_index = data.get('synopsis_index', 0)
    style = data.get('style', 'murakami')
    chapter = data.get('chapter', 1)
    direction = data.get('direction', '')
    
    if not synopsis_id:
        return jsonify({"error": "あらすじIDが必要です"})
    
    result = story_service.generate_story(
        synopsis_id, synopsis_index, model="grok", style=style, chapter=chapter,
        direction=direction
    )
    return jsonify(result)

@app.route('/api/enhance_story', methods=['POST'])
def api_enhance_story():
    """ストーリー強化API"""
    data = request.json
    story_id = data.get('story_id')
    options = data.get('options', {})
    
    if not story_id:
        return jsonify({"error": "ストーリーIDが必要です"})
    
    result = enhancement_service.enhance_story(story_id, options)
    return jsonify(result)

@app.route('/api/scene_prompts', methods=['POST'])
def api_generate_scene_prompts():
    """シーンプロンプト生成API"""
    data = request.json
    story_id = data.get('story_id')
    num_scenes = data.get('num_scenes', 3)
    
    if not story_id:
        return jsonify({"error": "ストーリーIDが必要です"})
    
    # ストーリーデータを取得
    story_data = story_service.load_story(story_id)
    if not story_data:
        return jsonify({"error": "指定されたストーリーが見つかりません"})
    
    # シーンプロンプトを生成
    story_text = story_data.get('text', '')
    prompts_text = enhancement_service.generate_scene_prompts(story_text, num_scenes)
    
    # プロンプトを保存
    filepath = enhancement_service.save_scene_prompts(story_id, prompts_text)
    
    return jsonify({
        "story_id": story_id,
        "prompts_text": prompts_text,
        "filepath": filepath
    })

if __name__ == '__main__':
    # データディレクトリの作成
    os.makedirs('data/settings', exist_ok=True)
    os.makedirs('data/synopses', exist_ok=True)
    os.makedirs('data/stories', exist_ok=True)
    os.makedirs('data/prompts', exist_ok=True)
    
    app.run(debug=True)