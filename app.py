# -*- coding: utf-8 -*- # 日本語コメントのため
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from markupsafe import Markup
import os
import re

# --- サービスのインポート ---
from services import setting_service, synopsis_service, story_service, enhancement_service
# --- Claude指示による追加インポート ---
from services import dialog_service # セリフ強化用
from api.ai_handler import ai_handler # AIモデルハンドラー

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Claude指示による定数定義（仮） ---
# 実際には設定ファイルやdialog_serviceから取得するのが望ましい
DIALOG_ENHANCEMENT_PRESETS = {
    'standard': '標準プリセット',
    'intense': '強調プリセット',
    'poetic': '詩的プリセット'
}
EROTIC_DIALOG_PATTERNS = [
    {'id': 'breathing', 'name': '息遣い'},
    {'id': 'moans', 'name': '喘ぎ声'},
    {'id': 'whispers', 'name': '囁き'}
]

# nl2brフィルター追加（改行をHTMLのbrタグに変換する）
@app.template_filter('nl2br')
def nl2br_filter(text):
    if not text:
        return ""
    return Markup(str(text).replace('\n', '<br>'))

# --- ヘルパー関数: 現在のAIモデル名を取得 ---
def get_current_model_name():
    """ai_handlerから現在のモデル名を取得、失敗時はデフォルトを返す"""
    try:
        # get_current_api_info()が辞書を返し、'name'キーを持つことを期待
        info = ai_handler.get_current_api_info()
        return info.get('name', 'grok') # nameキーがない場合もgrokにフォールバック
    except Exception as e:
        print(f"Error getting current model name: {e}") # エラーログ
        return 'grok' # 例外発生時もgrokにフォールバック

@app.route('/')
def index():
    """トップページ"""
    # AIモデル情報を取得してテンプレートに渡す (どのページでも選択できるようにする場合)
    try:
        available_models = ai_handler.get_available_models()
        current_model = ai_handler.get_current_api_info()
    except Exception as e:
        print(f"Error getting AI model info for index: {e}")
        available_models = []
        current_model = {'name': 'grok', 'description': 'Grok (デフォルト)'} # フォールバック
        flash("AIモデル情報の取得に失敗しました。デフォルトモデルを使用します。", "warning")

    return render_template('index.html',
                           ai_models=available_models,
                           current_model=current_model)

@app.route('/custom_setting', methods=['POST'])
def custom_setting():
    """カスタム設定からの生成処理"""
    if request.method == 'POST':
        custom_scenario = request.form.get('custom_scenario', '')
        current_model_name = get_current_model_name() # 現在のモデル名を取得

        # カスタムシナリオをもとに設定を生成
        result = setting_service.generate_setting_from_scenario(
            model=current_model_name, # 動的に取得したモデル名を使用
            scenario=custom_scenario
        )

        # エラーチェック
        if "error" in result.get("setting", {}):
            error_message = result['setting'].get('error', '不明なエラー')
            flash(f"設定の生成中にエラーが発生しました ({current_model_name}): {error_message}")
            return redirect(url_for('index'))

        # セッションに保存
        session['setting_id'] = result['id']

        # あらすじに直接進む
        return redirect(url_for('synopsis_direct'))

    return redirect(url_for('index'))

@app.route('/setting', methods=['GET', 'POST'])
def setting():
    """設定ジェネレーターページ"""
    # AIモデル情報を取得 (GET/POST共通)
    try:
        available_models = ai_handler.get_available_models()
        current_model = ai_handler.get_current_api_info()
    except Exception as e:
        print(f"Error getting AI model info for setting: {e}")
        available_models = []
        current_model = {'name': 'grok', 'description': 'Grok (デフォルト)'}
        flash("AIモデル情報の取得に失敗しました。", "warning")

    if request.method == 'POST':
        # フォームからデータを取得
        setting_type = request.form.get('setting_type', '一般')
        additional_details = request.form.get('additional_details', '')
        current_model_name = get_current_model_name() # 現在のモデル名を取得

        # 設定を生成
        result = setting_service.generate_setting(
            model=current_model_name, # 動的に取得したモデル名を使用
            setting_type=setting_type,
            additional_details=additional_details
            )

        # エラーチェック
        if "error" in result.get("setting", {}):
            error_message = result['setting'].get('error', '不明なエラー')
            flash(f"設定の生成中にエラーが発生しました ({current_model_name}): {error_message}")
            return render_template('setting.html',
                                   ai_models=available_models,
                                   current_model=current_model)

        # セッションに保存
        session['setting_id'] = result['id']

        # あらすじページにリダイレクト
        return redirect(url_for('synopsis'))

    # GETリクエスト
    return render_template('setting.html',
                           ai_models=available_models,
                           current_model=current_model)

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

    current_model_name = get_current_model_name() # 現在のモデル名を取得

    # あらすじを自動生成
    synopsis_result = synopsis_service.generate_synopses(
        setting_id,
        model=current_model_name, # 動的に取得したモデル名を使用
        style="murakami", # スタイルは別途選択可能にするかも？
        num_synopses=1
    )

    # エラーチェック（あらすじ生成）
    synopses = synopsis_result.get('synopses', [])
    if "error" in synopsis_result or (isinstance(synopses, dict) and "error" in synopses):
        error_message = synopsis_result.get("error") or synopses.get("error", "不明なエラー")
        flash(f"あらすじの生成中にエラーが発生しました ({current_model_name}): {error_message}")
        # AIモデル情報を取得してエラー表示ページへ
        try:
            available_models = ai_handler.get_available_models()
            current_model = ai_handler.get_current_api_info()
        except Exception as e:
            available_models, current_model = [], {'name': 'grok', 'description': 'Grok (デフォルト)'}
        return render_template('synopsis.html', setting=setting_data, ai_models=available_models, current_model=current_model)

    if not isinstance(synopses, list):
        if isinstance(synopses, dict) and "error" not in synopses:
             synopses = [synopses]
        else:
             synopses = []

    if 'id' in synopsis_result:
        session['synopsis_id'] = synopsis_result['id']
    else:
        flash("あらすじ情報の保存に失敗しました。")
        try:
            available_models = ai_handler.get_available_models()
            current_model = ai_handler.get_current_api_info()
        except Exception as e:
            available_models, current_model = [], {'name': 'grok', 'description': 'Grok (デフォルト)'}
        return render_template('synopsis.html', setting=setting_data, synopses=synopses, ai_models=available_models, current_model=current_model)

    # あらすじがあれば1話目を自動生成
    if synopses and len(synopses) > 0:
        story_result = story_service.generate_story(
            synopsis_result['id'], 0,
            model=current_model_name, # 動的に取得したモデル名を使用
            style="murakami", # スタイルも動的に？
            chapter=1
        )

        # エラーチェック（小説生成）
        if "error" in story_result:
             error_message = story_result.get('error', '不明なエラー')
             flash(f"第1話の生成中にエラーが発生しました ({current_model_name}): {error_message}")
             try:
                 available_models = ai_handler.get_available_models()
                 current_model = ai_handler.get_current_api_info()
             except Exception as e:
                 available_models, current_model = [], {'name': 'grok', 'description': 'Grok (デフォルト)'}
             return render_template(
                'synopsis.html',
                synopses=synopses,
                setting=setting_data,
                auto_generated=True,
                ai_models=available_models,
                current_model=current_model
            )

        # 1話目の生成に成功したら、直接小説ページへ
        # AIモデル情報を取得してstory.htmlへ渡す
        try:
            available_models = ai_handler.get_available_models()
            current_model = ai_handler.get_current_api_info()
        except Exception as e:
            available_models, current_model = [], {'name': 'grok', 'description': 'Grok (デフォルト)'}
            flash("AIモデル情報の取得に失敗しました。", "warning")

        return render_template(
            'story.html',
            story=story_result, # story_result には id (story_id) が含まれる想定
            synopsis_index=0,
            style="murakami",
            ai_models=available_models,
            current_model=current_model
        )

    # あらすじのみ生成成功の場合
    try:
        available_models = ai_handler.get_available_models()
        current_model = ai_handler.get_current_api_info()
    except Exception as e:
        available_models, current_model = [], {'name': 'grok', 'description': 'Grok (デフォルト)'}
    return render_template(
        'synopsis.html',
        synopses=synopses,
        setting=setting_data,
        auto_generated=True,
        ai_models=available_models,
        current_model=current_model
    )

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

    # AIモデル情報を取得 (GET/POST共通)
    try:
        available_models = ai_handler.get_available_models()
        current_model = ai_handler.get_current_api_info()
    except Exception as e:
        print(f"Error getting AI model info for synopsis: {e}")
        available_models = []
        current_model = {'name': 'grok', 'description': 'Grok (デフォルト)'}
        flash("AIモデル情報の取得に失敗しました。", "warning")

    if request.method == 'POST':
        style = request.form.get('style', 'murakami')
        current_model_name = get_current_model_name() # 現在のモデル名を取得

        result = synopsis_service.generate_synopses(
            setting_id,
            model=current_model_name, # 動的に取得したモデル名を使用
            style=style, num_synopses=1
        )

        synopses = result.get('synopses', [])
        if "error" in result or (isinstance(synopses, dict) and "error" in synopses):
            error_message = result.get("error") or synopses.get("error", "不明なエラー")
            flash(f"あらすじの生成中にエラーが発生しました ({current_model_name}): {error_message}")
            return render_template('synopsis.html', setting=setting_data, ai_models=available_models, current_model=current_model)

        if not isinstance(synopses, list):
            if isinstance(synopses, dict) and "error" not in synopses:
                synopses = [synopses]
            else:
                synopses = []

        if 'id' in result:
            session['synopsis_id'] = result['id']
        else:
            flash("あらすじ情報の保存に失敗しました。")
            return render_template(
                'synopsis.html',
                synopses=synopses,
                setting=setting_data,
                ai_models=available_models,
                current_model=current_model
            )

        return render_template(
            'synopsis.html',
            synopses=synopses,
            setting=setting_data,
            ai_models=available_models,
            current_model=current_model
        )

    # GETリクエスト
    return render_template('synopsis.html',
                           setting=setting_data,
                           ai_models=available_models,
                           current_model=current_model)

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

    # --- AIモデル情報の取得 (GET/POST共通) ---
    try:
        available_models = ai_handler.get_available_models()
        current_model_info = ai_handler.get_current_api_info()
    except Exception as e:
        print(f"Error getting AI model info for story: {e}")
        available_models = []
        current_model_info = {'name': 'grok', 'description': 'Grok (デフォルト)'}
        flash("AIモデル情報の取得に失敗しました。", "warning")
    # --- ここまで ---

    if request.method == 'POST':
        style = request.form.get('style', 'murakami')
        synopsis_index = int(request.form.get('synopsis_index', 0))
        chapter = int(request.form.get('chapter', 1))
        next_chapter_direction = request.form.get('next_chapter_direction', '')
        explicitness_level = int(request.form.get('explicitness_level', 3))
        selected_presets = request.form.getlist('presets')
        current_model_name = get_current_model_name() # 現在のモデル名を取得

        preset_text = ""
        if selected_presets:
            preset_text = "選択されたプリセット: " + ", ".join(selected_presets)
            next_chapter_direction = f"{next_chapter_direction}\n{preset_text}".strip()

        if next_chapter_direction:
            literary_directive = "\n【重要】性的描写は村上龍のような文学的表現を用い、年齢表記やバストサイズなどの直接的な数値表現は避けてください。徹底的な描写と比喩表現で読者の創造性を掻き立てる表現にしてください。"
            next_chapter_direction += literary_directive

        enhance_options = {
            "enhance_psychology": request.form.get('enhance_psychology') == 'on',
            "enhance_emotions": request.form.get('enhance_emotions') == 'on',
            "enhance_sensory": request.form.get('enhance_sensory') == 'on',
            "enhance_voice": request.form.get('enhance_voice') == 'on',
            "add_psychological_themes": request.form.get('add_psychological_themes') == 'on',
            "explicitness_level": explicitness_level
        }

        result = story_service.generate_story(
            synopsis_id, synopsis_index,
            model=current_model_name, # 動的に取得したモデル名を使用
            style=style, chapter=chapter,
            direction=next_chapter_direction, enhance_options=enhance_options
        )

        if "error" in result:
            error_message = result.get('error', '不明なエラー')
            flash(f"小説の生成中にエラーが発生しました ({current_model_name}): {error_message}")
            # エラー時も AI モデル情報を渡す
            return render_template(
                 'story.html',
                 error=error_message,
                 synopses=synopsis_data.get('synopses'),
                 setting_id=synopsis_data.get('setting_id'),
                 synopsis_index=synopsis_index,
                 style=style,
                 ai_models=available_models, # POST開始時に取得した情報
                 current_model=current_model_info # POST開始時に取得した情報
            )

        # --- Claude指示: テンプレートレンダリング時に引数を追加 ---
        # 小説表示 (成功時)
        return render_template(
            'story.html',
            story=result, # result には id (story_id) が含まれる想定
            synopsis_index=synopsis_index,
            style=style,
            enhanced=any(v for k, v in enhance_options.items() if k != 'explicitness_level'), # enhance_* or add_* がONならTrue
            ai_models=available_models, # POST開始時に取得した情報
            current_model=current_model_info # POST開始時に取得した情報
        )
        # --- ここまで ---

    # GETリクエストの場合
    # 最後に生成されたストーリーなどを表示する場合、ここで読み込む
    # last_story = story_service.load_last_story_for_synopsis(synopsis_id) # 仮
    last_story = None # ここでは単純化のため未実装

    # --- Claude指示: テンプレートレンダリング時に引数を追加 ---
    return render_template(
        'story.html',
        synopses=synopsis_data.get('synopses'),
        setting_id=synopsis_data.get('setting_id'),
        last_story=last_story, # 表示する場合
        # 次の章番号などを計算して渡す
        # next_chapter = len(last_story['chapters']) + 1 if last_story and 'chapters' in last_story else 1
        ai_models=available_models, # GET開始時に取得した情報
        current_model=current_model_info # GET開始時に取得した情報
    )
    # --- ここまで ---


# --- Claude指示による新しいルート: セリフ強化 ---
@app.route('/enhance_dialog/<story_id>', methods=['GET', 'POST'])
def enhance_dialog(story_id):
    """セリフ強化ページ"""
    # story_id を使って物語データを取得 (story_service に load_story(story_id) が必要)
    try:
        # story_service.load_story は指定されたIDの物語データ（辞書など）を返す想定
        story_data = story_service.load_story(story_id)
        if not story_data:
            flash(f"指定された物語(ID: {story_id})が見つかりません")
            return redirect(url_for('index')) # または適切なエラーページへ
    except Exception as e:
        flash(f"物語データの読み込み中にエラーが発生しました: {e}")
        return redirect(url_for('index')) # または適切なエラーページへ

    # AIモデル情報 (表示用)
    try:
        available_models = ai_handler.get_available_models()
        current_model = ai_handler.get_current_api_info()
    except Exception as e:
        available_models, current_model = [], {'name': 'grok', 'description': 'Grok (デフォルト)'}
        flash("AIモデル情報の取得に失敗しました。", "warning")


    if request.method == 'POST':
        # フォームからデータを取得
        preset = request.form.get('preset', 'standard')
        # getlistは空の場合に空リストを返す
        custom_patterns = request.form.getlist('pattern_types')
        custom_intensity = int(request.form.get('intensity', 3))
        current_model_name = get_current_model_name() # 現在のモデル名を取得 (強化に使う場合)

        # セリフ強化を実行 (dialog_serviceがモデル名を受け取るかはdialog_serviceの実装による)
        # dialog_service.enhance_erotic_dialog は強化後の story データ (または一部) を返す想定
        result = dialog_service.enhance_erotic_dialog(
            story_id=story_id,
            # model=current_model_name, # 必要であればモデル名を渡す
            preset=preset,
            custom_patterns=custom_patterns if custom_patterns else None, # 空リストはNoneとして渡すか、そのまま渡すかはdialog_serviceの仕様による
            custom_intensity=custom_intensity
        )

        # エラーチェック
        if "error" in result:
            error_message = result.get('error', '不明なエラー')
            flash(f"セリフ強化中にエラーが発生しました: {error_message}")
            # エラー発生時もフォームを表示するために元のテンプレートをレンダリング
            return render_template(
                'dialog_enhance.html', # セリフ強化用テンプレート
                story=story_data, # 元のストーリーデータ
                presets=DIALOG_ENHANCEMENT_PRESETS, # 定義したプリセット
                patterns=EROTIC_DIALOG_PATTERNS, # 定義したパターン
                # エラー発生時のフォーム値を復元するならここで渡す
                selected_preset=preset,
                selected_patterns=custom_patterns,
                selected_intensity=custom_intensity,
                ai_models=available_models,
                current_model=current_model
            )

        # 強化結果を story.html で表示
        # result が完全な story オブジェクト/辞書を返すことを想定
        flash("セリフを強化しました。")
        return render_template(
            'story.html', # 通常のストーリー表示テンプレート
            story=result, # 強化後のストーリーデータ
            enhanced=True, # 強化済みフラグ
            # story.html が synopsis_index や style を必要とする場合、
            # 元の story_data から取得するか、result に含める必要がある
            # synopsis_index=story_data.get('synopsis_index', 0), # 例
            # style=story_data.get('style', 'murakami'), # 例
            ai_models=available_models,
            current_model=current_model
        )

    # GETリクエストの場合: セリフ強化設定ページを表示
    return render_template(
        'dialog_enhance.html', # セリフ強化用テンプレート
        story=story_data, # 現在のストーリーデータ
        presets=DIALOG_ENHANCEMENT_PRESETS, # 定義したプリセット
        patterns=EROTIC_DIALOG_PATTERNS, # 定義したパターン
        ai_models=available_models,
        current_model=current_model
    )
# --- ここまで: セリフ強化ルート ---


# --- Claude指示による新しいルート: AIモデル選択 ---
@app.route('/select_model', methods=['POST'])
def select_model():
    """AIモデルを選択する"""
    if request.method == 'POST':
        model_name = request.form.get('model') # 'grok', 'claude', etc.

        if not model_name:
             flash("モデル名が選択されていません。", "error")
             # リファラーがなければインデックスへ
             return redirect(request.referrer or url_for('index'))

        try:
            # ai_handler.set_api を呼び出す
            success = ai_handler.set_api(model_name)

            if success:
                # 成功したら現在のモデル情報を取得して表示
                current_info = ai_handler.get_current_api_info()
                flash(f"AIモデルを '{current_info.get('description', model_name)}' に変更しました", "success")
            else:
                # set_apiがFalseを返した場合（ハンドラ内でエラー処理されている想定）
                 flash(f"AIモデル '{model_name}' の設定に失敗しました。利用可能か確認してください。", "error")

        except Exception as e:
             # set_apiやget_current_api_infoで予期せぬ例外が発生した場合
             flash(f"AIモデル変更中にエラーが発生しました: {e}", "error")
             print(f"Error during model selection: {e}") # ログにも出力

        # リファラーヘッダーから元のページに戻る（なければインデックスへ）
        # セキュリティのため、リファラーが自分のサイト内かチェックする方がより安全
        referrer = request.referrer
        # if referrer and is_safe_url(referrer): # is_safe_url は自作する必要あり
        #    return redirect(referrer)
        # return redirect(url_for('index'))
        # 今回は単純にリファラーへリダイレクト
        return redirect(referrer or url_for('index'))

    # POST以外は許可しない（またはindexへリダイレクト）
    return redirect(url_for('index'))
# --- ここまで: AIモデル選択ルート ---


# --- APIエンドポイント (変更なし、ただしmodel部分は同様に修正可能) ---
@app.route('/api/settings', methods=['POST'])
def api_generate_setting():
    """設定生成API"""
    data = request.json
    if not data: return jsonify({"error": "リクエストボディが空です"}), 400
    setting_type = data.get('setting_type', '一般')
    additional_details = data.get('additional_details', '')
    current_model_name = get_current_model_name() # APIでも選択中のモデルを使う

    result = setting_service.generate_setting(model=current_model_name, setting_type=setting_type, additional_details=additional_details)
    if "error" in result.get("setting", {}):
         return jsonify({"error": f"設定生成エラー: {result['setting'].get('error', '不明なエラー')}"}), 500
    return jsonify(result)

@app.route('/api/synopses', methods=['POST'])
def api_generate_synopses():
    """あらすじ生成API"""
    data = request.json
    if not data: return jsonify({"error": "リクエストボディが空です"}), 400
    setting_id = data.get('setting_id')
    style = data.get('style', 'murakami')
    num_synopses = data.get('num_synopses', 1)
    current_model_name = get_current_model_name() # APIでも選択中のモデルを使う

    if not setting_id: return jsonify({"error": "設定ID (setting_id) が必要です"}), 400

    result = synopsis_service.generate_synopses(setting_id, model=current_model_name, style=style, num_synopses=num_synopses)
    synopses = result.get('synopses', [])
    if "error" in result or (isinstance(synopses, dict) and "error" in synopses):
         error_message = result.get("error") or synopses.get("error", "不明なエラー")
         return jsonify({"error": f"あらすじ生成エラー: {error_message}"}), 500
    return jsonify(result)

@app.route('/api/stories', methods=['POST'])
def api_generate_story():
    """小説生成API"""
    data = request.json
    if not data: return jsonify({"error": "リクエストボディが空です"}), 400

    synopsis_id = data.get('synopsis_id')
    synopsis_index = data.get('synopsis_index', 0)
    style = data.get('style', 'murakami')
    chapter = data.get('chapter', 1)
    direction = data.get('direction', '')
    enhance_options = data.get('enhance_options', {})
    explicitness_level = data.get('explicitness_level', enhance_options.get('explicitness_level', 3))
    current_model_name = get_current_model_name() # APIでも選択中のモデルを使う

    if not synopsis_id: return jsonify({"error": "あらすじID (synopsis_id) が必要です"}), 400

    if direction:
        literary_directive = "\n【重要】性的描写は村上龍のような文学的表現を用い、年齢表記やバストサイズなどの直接的な数値表現は避けてください。徹底的な描写と比喩表現で読者の創造性を掻き立てる表現にしてください。"
        direction += literary_directive

    if "explicitness_level" not in enhance_options:
        enhance_options["explicitness_level"] = explicitness_level

    result = story_service.generate_story(
        synopsis_id, synopsis_index, model=current_model_name, style=style, chapter=chapter,
        direction=direction, enhance_options=enhance_options
    )
    if "error" in result:
         error_message = result.get('error', '不明なエラー')
         return jsonify({"error": f"小説生成エラー: {error_message}"}), 500
    return jsonify(result)

# --- アプリケーション実行 ---
if __name__ == '__main__':
    # データディレクトリの作成
    os.makedirs('data/settings', exist_ok=True)
    os.makedirs('data/synopses', exist_ok=True)
    os.makedirs('data/stories', exist_ok=True)

    # ai_handler の初期化（必要であれば）
    # ai_handler.initialize() # 例

    app.run(debug=True, host='0.0.0.0', port=5000)