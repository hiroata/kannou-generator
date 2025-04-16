from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import os
from services import setting_service, synopsis_service, story_service

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    """トップページ"""
    return render_template('index.html')

@app.route('/setting', methods=['GET', 'POST'])
def setting():
    """設定ジェネレーターページ"""
    if request.method == 'POST':
        # フォームからデータを取得
        model = request.form.get('model', 'gemini')
        setting_type = request.form.get('setting_type', '一般')
        additional_details = request.form.get('additional_details', '')
        
        # 設定を生成
        result = setting_service.generate_setting(model, setting_type, additional_details)
        
        # エラーチェック
        if "error" in result.get("setting", {}):
            flash(f"設定の生成中にエラーが発生しました: {result['setting'].get('error')}")
            return render_template('setting.html')
            
        # セッションに保存
        session['setting_id'] = result['id']
        
        # あらすじページにリダイレクト
        return redirect(url_for('synopsis'))
    
    return render_template('setting.html')

@app.route('/synopsis', methods=['GET', 'POST'])
def synopsis():
    """あらすじページ"""
    setting_id = session.get('setting_id')
    if not setting_id:
        return redirect(url_for('setting'))
    
    if request.method == 'POST':
        # フォームからデータを取得
        model = request.form.get('model', 'gemini')
        style = request.form.get('style', 'murakami')
        
        # あらすじを生成
        result = synopsis_service.generate_synopses(setting_id, model, style)
        
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
        model = request.form.get('model', 'gemini')
        style = request.form.get('style', 'murakami')
        synopsis_index = int(request.form.get('synopsis_index', 0))
        chapter = int(request.form.get('chapter', 1))
        
        # 小説を生成
        result = story_service.generate_story(
            synopsis_id, synopsis_index, model, style, chapter
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
        return render_template('story.html', story=result)
    
    # あらすじデータを取得
    synopsis_data = synopsis_service.load_synopsis(synopsis_id)
    
    return render_template(
        'story.html',
        synopses=synopsis_data.get('synopses'),
        setting_id=synopsis_data.get('setting_id')
    )

@app.route('/api/settings', methods=['POST'])
def api_generate_setting():
    """設定生成API"""
    data = request.json
    model = data.get('model', 'gemini')
    setting_type = data.get('setting_type', '一般')
    additional_details = data.get('additional_details', '')
    
    result = setting_service.generate_setting(model, setting_type, additional_details)
    return jsonify(result)

@app.route('/api/synopses', methods=['POST'])
def api_generate_synopses():
    """あらすじ生成API"""
    data = request.json
    setting_id = data.get('setting_id')
    model = data.get('model', 'gemini')
    style = data.get('style', 'murakami')
    
    if not setting_id:
        return jsonify({"error": "設定IDが必要です"})
    
    result = synopsis_service.generate_synopses(setting_id, model, style)
    return jsonify(result)

@app.route('/api/stories', methods=['POST'])
def api_generate_story():
    """小説生成API"""
    data = request.json
    synopsis_id = data.get('synopsis_id')
    synopsis_index = data.get('synopsis_index', 0)
    model = data.get('model', 'gemini')
    style = data.get('style', 'murakami')
    chapter = data.get('chapter', 1)
    
    if not synopsis_id:
        return jsonify({"error": "あらすじIDが必要です"})
    
    result = story_service.generate_story(
        synopsis_id, synopsis_index, model, style, chapter
    )
    return jsonify(result)

if __name__ == '__main__':
    # データディレクトリの作成
    os.makedirs('data/settings', exist_ok=True)
    os.makedirs('data/synopses', exist_ok=True)
    os.makedirs('data/stories', exist_ok=True)
    
    app.run(debug=True)