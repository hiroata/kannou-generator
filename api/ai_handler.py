# api/ai_handler.py - これを全文コピペして新しいファイルを作成してください
import importlib
from config import GROK_MODEL, OPENAI_MODEL, CLAUDE_MODEL, GEMINI_MODEL

class AIHandler:
    """
    各種AI APIを統一インターフェースで扱うクラス
    """
    
    def __init__(self):
        """
        利用可能なAIモデルとそのAPI実装を初期化
        """
        self.available_models = {
            "grok": {
                "api_module": "api.grok_api",
                "default_model": GROK_MODEL,
                "description": "X.AI Grok-3 (デフォルト)"
            },
            "openai": {
                "api_module": "api.openai_api",
                "default_model": OPENAI_MODEL,
                "description": "OpenAI GPT-4o"
            },
            "claude": {
                "api_module": "api.claude_api",
                "default_model": CLAUDE_MODEL,
                "description": "Anthropic Claude-3"
            },
            "gemini": {
                "api_module": "api.gemini_api",
                "default_model": GEMINI_MODEL,
                "description": "Google Gemini-1.5"
            }
        }
        
        # 実際に使用可能なAPIモジュールを確認
        self.supported_apis = {}
        for api_name, api_info in self.available_models.items():
            try:
                # モジュールの動的インポートを試みる
                module = importlib.import_module(api_info["api_module"])
                if hasattr(module, "generate_text"):
                    self.supported_apis[api_name] = api_info
            except (ImportError, ModuleNotFoundError):
                # モジュールが存在しない場合はスキップ
                print(f"Warning: API module {api_info['api_module']} not found")
        
        # デフォルトのAPIをGrokに設定
        self.current_api = "grok"
    
    def get_available_models(self):
        """利用可能なAIモデルのリストを返す"""
        return {name: info["description"] for name, info in self.supported_apis.items()}
    
    def set_api(self, api_name):
        """
        使用するAPIを設定する
        
        Args:
            api_name (str): APIの名前 ('grok', 'openai', 'claude', 'gemini')
            
        Returns:
            bool: 設定が成功したかどうか
        """
        if api_name in self.supported_apis:
            self.current_api = api_name
            return True
        return False
    
    def generate_text(self, prompt, max_tokens=2000, temperature=0.7):
        """
        選択されたAPIを使用してテキストを生成する
        
        Args:
            prompt (str): 生成プロンプト
            max_tokens (int): 生成する最大トークン数
            temperature (float): 生成の多様性を制御するパラメータ
            
        Returns:
            str: 生成されたテキスト
        """
        if self.current_api not in self.supported_apis:
            return f"エラー: 選択されたAPI '{self.current_api}' はサポートされていません"
        
        try:
            # 動的にAPIモジュールを読み込んで実行
            api_info = self.supported_apis[self.current_api]
            module = importlib.import_module(api_info["api_module"])
            
            # max_tokensを調整（各APIの制限に合わせる）
            adjusted_max_tokens = max_tokens
            if self.current_api == "claude" and max_tokens > 4000:
                adjusted_max_tokens = 4000
            
            # generate_text関数を呼び出す
            return module.generate_text(prompt, max_tokens=adjusted_max_tokens, temperature=temperature)
            
        except Exception as e:
            return f"テキスト生成エラー: {str(e)}"
    
    def get_current_api_info(self):
        """現在選択されているAPIの情報を返す"""
        if self.current_api in self.supported_apis:
            return {
                "name": self.current_api,
                "description": self.supported_apis[self.current_api]["description"],
                "default_model": self.supported_apis[self.current_api]["default_model"]
            }
        return {"name": "unknown", "description": "Unknown API", "default_model": ""}

# グローバルなAIハンドラーインスタンスを作成
ai_handler = AIHandler()

def generate_text(prompt, max_tokens=2000, temperature=0.7, api_name=None):
    """
    指定されたAPIを使用してテキストを生成するユーティリティ関数
    
    Args:
        prompt (str): 生成プロンプト
        max_tokens (int): 生成する最大トークン数
        temperature (float): 生成の多様性を制御するパラメータ
        api_name (str, optional): 使用するAPI名。指定がなければ現在のAPIを使用
        
    Returns:
        str: 生成されたテキスト
    """
    # 一時的にAPIを切り替える場合
    if api_name and api_name in ai_handler.supported_apis:
        current_api = ai_handler.current_api
        ai_handler.set_api(api_name)
        response = ai_handler.generate_text(prompt, max_tokens, temperature)
        ai_handler.set_api(current_api)
        return response
    
    # 現在設定されているAPIを使用
    return ai_handler.generate_text(prompt, max_tokens, temperature)