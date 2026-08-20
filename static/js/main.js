/**
 * AI Career Intelligence Platform - Frontend Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initFileUpload();
    initBulletRewriter();
    initHistoryAndComparison();
    initCharts();
});

// Tab Navigation
function initTabs() {
    const navItems = document.querySelectorAll('.nav-tab');
    const tabPanels = document.querySelectorAll('.tab-panel');

    navItems.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.getAttribute('data-tab');

            navItems.forEach(t => t.classList.remove('active'));
            tabPanels.forEach(p => p.classList.remove('active'));

            tab.classList.add('active');
            const targetPanel = document.getElementById(`tab-${target}`);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
}

// File Upload Drag & Drop & Name display
function initFileUpload() {
    const fileInput = document.getElementById('resume-upload');
    const fileNameDisplay = document.getElementById('file-name-display');
    const dropZone = document.getElementById('drop-zone');

    if (!fileInput || !dropZone) return;

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileNameDisplay.textContent = `📄 Selected: ${e.target.files[0].name}`;
            fileNameDisplay.style.color = 'var(--accent)';
            fileNameDisplay.style.fontWeight = '700';
        }
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--accent)';
            dropZone.style.background = 'rgba(0, 210, 255, 0.08)';
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropZone.style.borderColor = 'var(--glass-border)';
            dropZone.style.background = 'transparent';
        }, false);
    });
}

// Live Interactive AI Bullet Rewriter
function initBulletRewriter() {
    const btnRewrite = document.getElementById('btn-do-rewrite');
    const inputBullet = document.getElementById('input-bullet-rewrite');
    const resultBox = document.getElementById('rewrite-result-box');

    if (!btnRewrite || !inputBullet || !resultBox) return;

    btnRewrite.addEventListener('click', async () => {
        const text = inputBullet.value.trim();
        if (!text) {
            alert('Please enter a bullet point to rewrite.');
            return;
        }

        btnRewrite.disabled = true;
        btnRewrite.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Rewriting...';

        try {
            const res = await fetch('/api/rewrite-bullet', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ bullet: text })
            });

            const data = await res.json();
            btnRewrite.disabled = false;
            btnRewrite.innerHTML = '<i class="fas fa-magic"></i> Transform with STAR Method';

            if (data.rewritten) {
                renderRewriteResult(data, resultBox);
            }
        } catch (err) {
            btnRewrite.disabled = false;
            btnRewrite.innerHTML = '<i class="fas fa-magic"></i> Transform with STAR Method';
            alert('Error rewriting bullet point. Please try again.');
        }
    });
}

function renderRewriteResult(data, container) {
    let improvementsHtml = data.improvements.map(imp => `<li><i class="fas fa-check-circle"></i> ${imp}</li>`).join('');

    container.innerHTML = `
        <div class="rewrite-card">
            <div class="rewrite-comparison">
                <div class="rewrite-box original">
                    <span class="badge badge-passive">Original (Weak/Passive)</span>
                    <p>${escapeHtml(data.original)}</p>
                </div>
                <div class="rewrite-arrow"><i class="fas fa-arrow-right"></i></div>
                <div class="rewrite-box optimized">
                    <span class="badge badge-active">AI STAR Optimized</span>
                    <p id="optimized-bullet-text">${escapeHtml(data.rewritten)}</p>
                    <button class="btn-copy" onclick="copyToClipboard('optimized-bullet-text')">
                        <i class="fas fa-copy"></i> Copy
                    </button>
                </div>
            </div>
            <div class="rewrite-improvements">
                <h4><i class="fas fa-bolt"></i> AI Enhancements Applied:</h4>
                <ul>${improvementsHtml}</ul>
            </div>
        </div>
    `;
    container.style.display = 'block';
}

// Copy to Clipboard Utility
function copyToClipboard(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const text = el.innerText;
    navigator.clipboard.writeText(text).then(() => {
        alert('Copied to clipboard!');
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}

// History & Resume Version Comparison
function initHistoryAndComparison() {
    const currentAnalysis = window.ANALYSIS_DATA;
    if (currentAnalysis && currentAnalysis.comprehensive) {
        saveAnalysisToHistory(currentAnalysis);
    }
    renderHistoryUI();
}

function saveAnalysisToHistory(analysis) {
    let history = JSON.parse(localStorage.getItem('resume_analysis_history') || '[]');
    
    // Avoid duplicate entry if saved in same minute
    const timestamp = new Date().toLocaleString();
    const entry = {
        id: 'hist_' + Date.now(),
        date: timestamp,
        filename: analysis.filename || 'Resume.pdf',
        score: analysis.comprehensive.ats_score,
        jd_match: analysis.jd_match ? analysis.jd_match.match_percentage : null,
        skillsCount: analysis.comprehensive.all_skills ? analysis.comprehensive.all_skills.length : 0,
        fullData: analysis
    };

    // Keep last 10
    history.unshift(entry);
    history = history.slice(0, 10);
    localStorage.setItem('resume_analysis_history', JSON.stringify(history));
}

function renderHistoryUI() {
    const historyListContainer = document.getElementById('history-list-container');
    const compareSelectorA = document.getElementById('compare-select-a');
    const compareSelectorB = document.getElementById('compare-select-b');
    const btnCompare = document.getElementById('btn-run-compare');

    const history = JSON.parse(localStorage.getItem('resume_analysis_history') || '[]');

    if (historyListContainer) {
        if (history.length === 0) {
            historyListContainer.innerHTML = '<p class="text-muted">No analysis history yet. Upload a resume to begin tracking progress!</p>';
        } else {
            historyListContainer.innerHTML = history.map(item => `
                <div class="history-item-card">
                    <div class="hist-info">
                        <span class="hist-filename"><i class="fas fa-file-pdf"></i> ${escapeHtml(item.filename)}</span>
                        <span class="hist-date"><i class="far fa-clock"></i> ${item.date}</span>
                    </div>
                    <div class="hist-badges">
                        <span class="hist-score-badge">ATS Score: <strong>${item.score}%</strong></span>
                        ${item.jd_match ? `<span class="hist-jd-badge">JD Match: ${item.jd_match}%</span>` : ''}
                        <span class="hist-skills-badge">${item.skillsCount} Skills</span>
                    </div>
                </div>
            `).join('');
        }
    }

    if (compareSelectorA && compareSelectorB) {
        const optionsHtml = history.map(item => 
            `<option value="${item.id}">${item.filename} (${item.date}) - Score: ${item.score}%</option>`
        ).join('');

        compareSelectorA.innerHTML = '<option value="">Select Version A</option>' + optionsHtml;
        compareSelectorB.innerHTML = '<option value="">Select Version B</option>' + optionsHtml;

        if (btnCompare) {
            btnCompare.onclick = () => runVersionComparison(history);
        }
    }
}

function runVersionComparison(history) {
    const idA = document.getElementById('compare-select-a').value;
    const idB = document.getElementById('compare-select-b').value;
    const compareResultContainer = document.getElementById('compare-results-output');

    if (!idA || !idB) {
        alert('Please select two versions to compare.');
        return;
    }

    if (idA === idB) {
        alert('Please select two different versions for comparison.');
        return;
    }

    const itemA = history.find(i => i.id === idA);
    const itemB = history.find(i => i.id === idB);

    if (!itemA || !itemB) return;

    const dataA = itemA.fullData.comprehensive;
    const dataB = itemB.fullData.comprehensive;

    const scoreDiff = dataB.ats_score - dataA.ats_score;
    const diffClass = scoreDiff >= 0 ? 'text-success' : 'text-danger';
    const diffSign = scoreDiff >= 0 ? '+' : '';

    compareResultContainer.innerHTML = `
        <div class="comparison-grid">
            <div class="comp-column">
                <h3>Version A: ${escapeHtml(itemA.filename)}</h3>
                <p class="comp-date">${itemA.date}</p>
                <div class="comp-metric-card">
                    <span class="comp-metric-val">${dataA.ats_score}%</span>
                    <span class="comp-metric-lbl">ATS Score</span>
                </div>
                <div class="comp-skills-list">
                    <strong>Skills (${dataA.all_skills.length}):</strong>
                    <p>${dataA.all_skills.join(', ')}</p>
                </div>
            </div>

            <div class="comp-divider">
                <div class="comp-delta-badge ${diffClass}">
                    <span>Score Diff</span>
                    <h2>${diffSign}${scoreDiff}%</h2>
                </div>
            </div>

            <div class="comp-column">
                <h3>Version B: ${escapeHtml(itemB.filename)}</h3>
                <p class="comp-date">${itemB.date}</p>
                <div class="comp-metric-card">
                    <span class="comp-metric-val">${dataB.ats_score}%</span>
                    <span class="comp-metric-lbl">ATS Score</span>
                </div>
                <div class="comp-skills-list">
                    <strong>Skills (${dataB.all_skills.length}):</strong>
                    <p>${dataB.all_skills.join(', ')}</p>
                </div>
            </div>
        </div>
    `;
    compareResultContainer.style.display = 'block';
}

// Chart.js Visualization Engine
function initCharts() {
    if (typeof Chart === 'undefined') return;

    const currentAnalysis = window.ANALYSIS_DATA;

    // 1. Radar Chart for ATS Breakdown
    const radarCtx = document.getElementById('atsRadarChart');
    if (radarCtx && currentAnalysis && currentAnalysis.comprehensive) {
        const bd = currentAnalysis.comprehensive.score_breakdown;
        new Chart(radarCtx, {
            type: 'radar',
            data: {
                labels: ['Keywords & Skills', 'Formatting & Structure', 'Action Verbs', 'Quantifiable Metrics'],
                datasets: [{
                    label: 'ATS Sub-scores',
                    data: [bd.keywords, bd.formatting, bd.action_verbs, bd.impact_metrics],
                    backgroundColor: 'rgba(0, 210, 255, 0.25)',
                    borderColor: '#00d2ff',
                    pointBackgroundColor: '#92fe9d',
                    pointBorderColor: '#fff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        pointLabels: { color: '#ffffff', font: { family: 'Outfit', size: 12 } },
                        suggestedMin: 0,
                        suggestedMax: 100,
                        ticks: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // 2. Score History Trend Chart
    const historyCtx = document.getElementById('scoreHistoryChart');
    const history = JSON.parse(localStorage.getItem('resume_analysis_history') || '[]');

    if (historyCtx && history.length > 0) {
        const reversedHistory = [...history].reverse();
        const labels = reversedHistory.map((item, idx) => `V${idx + 1}`);
        const scores = reversedHistory.map(item => item.score);

        new Chart(historyCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'ATS Score Progress',
                    data: scores,
                    borderColor: '#8a2be2',
                    backgroundColor: 'rgba(138, 43, 226, 0.2)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointBackgroundColor: '#00d2ff'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#b0b0b0' } },
                    y: { min: 0, max: 100, grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#b0b0b0' } }
                },
                plugins: {
                    legend: { labels: { color: '#ffffff' } }
                }
            }
        });
    }
}

// Utility HTML escape helper
function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
