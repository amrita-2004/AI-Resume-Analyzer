document.addEventListener('DOMContentLoaded', () => {
    // 1. Dark / Light Theme Switcher
    const themeToggleBtn = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const htmlElement = document.documentElement;

    const savedTheme = localStorage.getItem('theme') || 'dark';
    htmlElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        if (themeIcon) {
            themeIcon.className = theme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
        }
    }

    // 2. File Upload Dropzone Name Display & Drag-and-Drop Interactivity
    const resumeInput = document.getElementById('resume-upload');
    const fileNameDisplay = document.getElementById('file-name-display');
    const dropZone = document.getElementById('drop-zone');

    if (resumeInput && fileNameDisplay) {
        resumeInput.addEventListener('change', (e) => {
            if (e.target.files && e.target.files.length > 0) {
                fileNameDisplay.textContent = `Selected File: ${e.target.files[0].name}`;
            }
        });
    }

    if (dropZone) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('drag-over');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('drag-over');
            }, false);
        });

        dropZone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files && files.length > 0 && resumeInput) {
                resumeInput.files = files;
                fileNameDisplay.textContent = `Selected File: ${files[0].name}`;
            }
        });
    }

    // 3. Sub-Tabs Switching Logic
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.getAttribute('data-tab');
            
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            const tabPanels = document.querySelectorAll('.tab-panel');
            tabPanels.forEach(panel => {
                panel.style.display = 'none';
                panel.classList.remove('active');
            });

            const activePanel = document.getElementById(`tab-${targetTab}`);
            if (activePanel) {
                activePanel.style.display = 'block';
                activePanel.classList.add('active');
            }
        });
    });
});

// Live Bullet Point Rewriter Tool
function rewriteBulletLive() {
    const input = document.getElementById('liveBulletInput');
    const resultCard = document.getElementById('bulletRewriteResult');
    const rewrittenText = document.getElementById('rewrittenBulletText');

    if (!input || !input.value.trim()) {
        alert("Please enter a bullet point to rewrite.");
        return;
    }

    fetch('/api/rewrite-bullet', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bullet: input.value.trim() })
    })
    .then(res => res.json())
    .then(data => {
        if (data.rewritten) {
            rewrittenText.textContent = data.rewritten;
            resultCard.style.display = 'block';
        } else if (data.error) {
            alert(data.error);
        }
    })
    .catch(err => {
        console.error(err);
        alert("Error invoking rewrite bullet API.");
    });
}
