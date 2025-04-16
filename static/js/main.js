// DOMの読み込み完了後に実行
document.addEventListener('DOMContentLoaded', function() {
    // 設定フォームの処理
    const settingForm = document.querySelector('form[action="/setting"]');
    if (settingForm) {
        settingForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = '生成中...';
        });
    }
    
    // あらすじフォームの処理
    const synopsisForm = document.querySelector('form[action="/synopsis"]');
    if (synopsisForm) {
        synopsisForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = '生成中...';
        });
    }
    
    // 小説生成フォームの処理（複数ある可能性）
    const storyForms = document.querySelectorAll('form[action="/story"]');
    if (storyForms.length > 0) {
        storyForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const submitBtn = this.querySelector('button[type="submit"]');
                submitBtn.disabled = true;
                submitBtn.textContent = '生成中...';
            });
        });
    }
    
    // 小説保存ボタンの処理
    const saveStoryBtn = document.getElementById('saveStory');
    if (saveStoryBtn) {
        saveStoryBtn.addEventListener('click', function() {
            const storyContent = document.querySelector('.story-content').textContent;
            
            // テキストファイルとして保存
            const blob = new Blob([storyContent], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = '官能小説.txt';
            a.click();
            
            URL.revokeObjectURL(url);
        });
    }
    
    // スタイル切り替えの視覚的フィードバック
    const styleSelects = document.querySelectorAll('select[name="style"]');
    if (styleSelects.length > 0) {
        styleSelects.forEach(select => {
            select.addEventListener('change', function() {
                const parentForm = this.closest('form');
                if (this.value === 'murakami') {
                    parentForm.style.borderLeft = '5px solid #2196F3';
                } else if (this.value === 'dan') {
                    parentForm.style.borderLeft = '5px solid #F44336';
                }
            });
        });
    }
    
    // モデル切り替えの視覚的フィードバック
    const modelSelects = document.querySelectorAll('select[name="model"]');
    if (modelSelects.length > 0) {
        modelSelects.forEach(select => {
            select.addEventListener('change', function() {
                const parentForm = this.closest('form');
                if (this.value === 'grok') {
                    parentForm.style.borderTop = '5px solid #000';
                } else if (this.value === 'gemini') {
                    parentForm.style.borderTop = '5px solid #4285F4';
                }
            });
        });
    }
});