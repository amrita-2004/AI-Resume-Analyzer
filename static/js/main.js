/**
 * AI Career Intelligence Platform - Frontend Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initFileUpload();
    initBulletRewriter();
    initHistoryAndComparison();
    initCharts();
    initRecoveryEngine();
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

// AI Job Readiness & Rejection Recovery Engine Frontend Interactivity
function initRecoveryEngine() {
    initRoadmapTabs();
    initReadinessTracker();
    initReanalysisForm();
}

// Roadmap 7/30/60/90-Day Tab Switcher
function initRoadmapTabs() {
    const tabs = document.querySelectorAll('.roadmap-tab');
    const panels = document.querySelectorAll('.roadmap-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const planDays = tab.getAttribute('data-plan');
            tabs.forEach(t => t.classList.remove('active'));
            panels.forEach(p => p.classList.remove('active'));

            tab.classList.add('active');
            const targetPanel = document.getElementById(`plan-panel-${planDays}`);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });
}

// Re-Application Readiness Progress Tracker Checkbox Engine
function initReadinessTracker() {
    const checkboxes = document.querySelectorAll('.task-checkbox');
    const trackerVal = document.getElementById('tracker-readiness-val');
    const trackerProgress = document.getElementById('tracker-progress-bar');
    const gaugeVal = document.getElementById('readiness-gauge-val');

    if (!checkboxes.length || !trackerVal) return;

    const initialScore = parseInt(trackerVal.innerText) || 50;

    checkboxes.forEach(cb => {
        cb.addEventListener('change', () => {
            let addedPoints = 0;
            checkboxes.forEach(c => {
                if (c.checked) {
                    addedPoints += (parseInt(c.getAttribute('data-weight')) || 15);
                }
            });

            // Scale score dynamically up to 98 max
            let updatedScore = Math.min(initialScore + Math.round((addedPoints / 100) * (98 - initialScore)), 98);
            
            trackerVal.innerText = `${updatedScore}%`;
            if (gaugeVal) gaugeVal.innerText = `${updatedScore}%`;
            if (trackerProgress) trackerProgress.style.width = `${updatedScore}%`;
        });
    });
}

// Resume Re-Analysis Form Submission Handler
function initReanalysisForm() {
    const form = document.getElementById('reanalyze-form');
    const btn = document.getElementById('btn-reanalyze');
    const fileInput = document.getElementById('reanalyze-file');
    const outputBox = document.getElementById('reanalyze-output-box');

    if (!form || !btn || !outputBox) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!fileInput.files.length) {
            alert('Please select an improved resume file to re-analyze.');
            return;
        }

        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Comparing Resumes...';

        const formData = new FormData();
        formData.append('resume', fileInput.files[0]);
        if (window.ANALYSIS_DATA) {
            formData.append('previous_analysis', JSON.stringify(window.ANALYSIS_DATA));
        }

        try {
            const res = await fetch('/api/reanalyze', {
                method: 'POST',
                body: formData
            });

            const data = await res.json();
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-rotate"></i> Re-Analyze My Resume';

            if (data.status === 'success' && data.comparison) {
                renderReanalysisResult(data.comparison, outputBox);
            } else {
                alert(data.error || 'Failed to re-analyze resume.');
            }
        } catch (err) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-rotate"></i> Re-Analyze My Resume';
            alert('Error connecting to server for re-analysis.');
        }
    });
}

function renderReanalysisResult(comp, container) {
    const diffSign = comp.improvement_pct >= 0 ? '+' : '';
    const diffClass = comp.improvement_pct >= 0 ? 'text-success' : 'text-danger';

    let gainedSkillsHtml = comp.gained_skills.length > 0 
        ? comp.gained_skills.map(s => `<span class="skill-tag prio-badge-low">${escapeHtml(s)}</span>`).join(' ') 
        : '<span class="text-muted">None detected</span>';

    let resolvedGapsHtml = comp.resolved_gaps.length > 0
        ? comp.resolved_gaps.map(s => `<span class="skill-tag prio-badge-med">${escapeHtml(s)}</span>`).join(' ')
        : '<span class="text-muted">None resolved</span>';

    container.innerHTML = `
        <div style="background: rgba(0, 210, 255, 0.05); border: 1px solid var(--accent); border-radius: 18px; padding: 1.5rem;">
            <h3 style="color: var(--accent); margin-bottom: 1rem;"><i class="fas fa-square-poll-vertical"></i> Resume Re-Analysis Delta Report</h3>
            
            <div class="comparison-grid" style="margin-top: 1rem;">
                <div class="comp-column">
                    <h3>Previous Analysis</h3>
                    <div class="comp-metric-card" style="text-align: center; margin: 1rem 0;">
                        <span class="comp-metric-val" style="font-size: 2.2rem; font-weight: 800;">${comp.previous_score}%</span>
                        <span class="comp-metric-lbl" style="display: block; color: var(--text-muted);">Baseline Readiness</span>
                    </div>
                </div>

                <div class="comp-divider">
                    <div class="comp-delta-badge ${diffClass}">
                        <span>Improvement</span>
                        <h2 style="font-size: 2.2rem; font-weight: 800;">${diffSign}${comp.improvement_pct}%</h2>
                    </div>
                </div>

                <div class="comp-column">
                    <h3>Current Analysis</h3>
                    <div class="comp-metric-card" style="text-align: center; margin: 1rem 0;">
                        <span class="comp-metric-val" style="font-size: 2.2rem; font-weight: 800; color: var(--accent-green);">${comp.current_score}%</span>
                        <span class="comp-metric-lbl" style="display: block; color: var(--text-muted);">Updated Readiness Tier: ${escapeHtml(comp.new_readiness_status)}</span>
                    </div>
                </div>
            </div>

            <div style="margin-top: 1.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="background: rgba(0, 0, 0, 0.2); padding: 1rem; border-radius: 12px;">
                    <strong style="color: var(--success);"><i class="fas fa-plus-circle"></i> Skills Gained (${comp.gained_skills.length}):</strong>
                    <div class="tags" style="margin-top: 0.5rem;">${gainedSkillsHtml}</div>
                </div>
                <div style="background: rgba(0, 0, 0, 0.2); padding: 1rem; border-radius: 12px;">
                    <strong style="color: var(--accent);"><i class="fas fa-check-double"></i> Skill Gaps Resolved (${comp.resolved_gaps.length}):</strong>
                    <div class="tags" style="margin-top: 0.5rem;">${resolvedGapsHtml}</div>
                </div>
            </div>
        </div>
    `;
    container.style.display = 'block';
}

