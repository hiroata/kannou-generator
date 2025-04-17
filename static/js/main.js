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
    
    // 指示プリセットの選択処理
    const presetOptions = document.querySelectorAll('.preset-option');
    const directionTextarea = document.getElementById('next-chapter-direction');
    
    if (presetOptions.length > 0 && directionTextarea) {
        presetOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                // 選択状態をトグル
                this.classList.toggle('selected');
                
                // 選択されたすべてのオプションのテキストを集める
                const selectedOptions = document.querySelectorAll('.preset-option.selected');
                let combinedText = '';
                
                selectedOptions.forEach(selected => {
                    const text = selected.getAttribute('data-text');
                    // 文の重複を避ける
                    if (text && !combinedText.includes(text)) {
                        combinedText += text + '\n\n';
                    }
                });
                
                // テキストエリアに設定
                directionTextarea.value = combinedText.trim();
            });
        });
    }
});