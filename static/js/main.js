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
    
    // 指示プリセットの処理
    initializePresetControls();
    
    // Explicitness Slider
    initializeExplicitnessSlider();
});

// プリセットコントロールの初期化
function initializePresetControls() {
    const presetLabels = document.querySelectorAll('.preset-label');
    const directionTextarea = document.getElementById('next-chapter-direction');
    
    if (presetLabels.length > 0 && directionTextarea) {
        presetLabels.forEach(label => {
            const checkbox = label.querySelector('input[type="checkbox"]');
            
            label.addEventListener('click', function(e) {
                // Prevent default only if clicking on the label itself, not the checkbox
                if (e.target !== checkbox) {
                    e.preventDefault();
                    checkbox.checked = !checkbox.checked;
                }
                
                // Toggle selected class
                if (checkbox.checked) {
                    label.classList.add('selected');
                } else {
                    label.classList.remove('selected');
                }
                
                // Update textarea content
                updateDirectionText();
            });
            
            // Also listen for direct checkbox changes
            if (checkbox) {
                checkbox.addEventListener('change', function() {
                    if (this.checked) {
                        label.classList.add('selected');
                    } else {
                        label.classList.remove('selected');
                    }
                    
                    updateDirectionText();
                });
            }
        });
        
        function updateDirectionText() {
            // Collect all selected presets
            const selectedPresets = document.querySelectorAll('.preset-label input[type="checkbox"]:checked');
            let combinedText = '';
            
            selectedPresets.forEach(preset => {
                const text = preset.getAttribute('data-text');
                // Avoid duplicate text
                if (text && !combinedText.includes(text)) {
                    combinedText += text + '\n\n';
                }
            });
            
            // Add literary quality enforcement
            if (combinedText) {
                combinedText += "\n【重要】性的描写は村上龍のような文学的表現を用い、年齢表記やバストサイズなどの直接的な数値表現は避けてください。徹底的な描写と比喩表現で読者の創造性を掻き立てる表現にしてください。\n";
            }
            
            // Set to textarea
            directionTextarea.value = combinedText.trim();
        }
    }
}

// 露骨さスライダーの初期化
function initializeExplicitnessSlider() {
    const explicitnessSlider = document.getElementById('explicitness-level');
    const explicitnessValue = document.getElementById('explicitness-value');
    
    if (explicitnessSlider && explicitnessValue) {
        // Set initial value
        explicitnessValue.textContent = explicitnessSlider.value;
        
        // Update on change
        explicitnessSlider.addEventListener('input', function() {
            explicitnessValue.textContent = this.value;
        });
    }
}