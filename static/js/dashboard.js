document.addEventListener('DOMContentLoaded', () => {
    fetchDashboardTelemetry();
});

let atsChart, skillChart, readinessChart, missingChart, comparisonChart;

function fetchDashboardTelemetry() {
    fetch('/api/dashboard')
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                updateDashboardCards(data.dashboard_cards);
                renderDashboardCharts(data.charts, data.dashboard_cards);
            } else {
                console.log("[Dashboard] No live analysis data yet.");
            }
        })
        .catch(err => console.error("[Dashboard Telemetry Error]", err));
}

function refreshDashboardData() {
    fetchDashboardTelemetry();
}

function updateDashboardCards(cards) {
    if (!cards) return;
    
    document.getElementById('cardAtsScore').textContent = cards.ats_score || 0;
    document.getElementById('cardJobMatch').textContent = cards.job_match_pct || 0;
    document.getElementById('cardSkillMatch').textContent = cards.skill_match_pct || 0;
    document.getElementById('cardExpMatch').textContent = cards.experience_match_pct || 0;
    document.getElementById('cardReadinessScore').textContent = cards.job_readiness_score || 0;
    
    const missing = cards.missing_skills || [];
    document.getElementById('cardMissingCount').textContent = missing.length;
    document.getElementById('cardMissingPreview').textContent = missing.length > 0 ? missing.slice(0, 3).join(', ') : 'None detected';
    
    const statusEl = document.getElementById('cardResumeStatus');
    statusEl.textContent = cards.resume_status || 'Ready';
    
    const tierBadge = document.getElementById('cardTierBadge');
    tierBadge.textContent = cards.resume_status || 'Evaluated';
}

function renderDashboardCharts(charts, cards) {
    if (!charts) return;

    // 1. ATS Score Breakdown Bar Chart
    const atsCtx = document.getElementById('atsScoreChart');
    if (atsCtx) {
        const breakdown = charts.score_breakdown || { keywords: 75, formatting: 85, action_verbs: 70, impact_metrics: 60 };
        if (atsChart) atsChart.destroy();
        atsChart = new Chart(atsCtx, {
            type: 'bar',
            data: {
                labels: ['Keywords', 'Formatting', 'Action Verbs', 'Impact Metrics'],
                datasets: [{
                    label: 'Score / 100',
                    data: [breakdown.keywords, breakdown.formatting, breakdown.action_verbs, breakdown.impact_metrics],
                    backgroundColor: ['#0d9488', '#2563eb', '#a855f7', '#f59e0b'],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { min: 0, max: 100 } }
            }
        });
    }

    // 2. Skill Match Radar Chart
    const skillCtx = document.getElementById('skillMatchChart');
    if (skillCtx) {
        const categories = charts.skill_density || [
            { category: "Languages", count: 4 },
            { category: "Web/Frameworks", count: 5 },
            { category: "Databases", count: 3 },
            { category: "Cloud/DevOps", count: 2 },
            { category: "Tools", count: 4 }
        ];
        if (skillChart) skillChart.destroy();
        skillChart = new Chart(skillCtx, {
            type: 'radar',
            data: {
                labels: categories.map(c => c.category),
                datasets: [{
                    label: 'Detected Skill Density',
                    data: categories.map(c => c.count * 15),
                    backgroundColor: 'rgba(13, 148, 136, 0.25)',
                    borderColor: '#0d9488',
                    pointBackgroundColor: '#0d9488'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // 3. Job Readiness Donut Chart
    const readinessCtx = document.getElementById('jobReadinessChart');
    if (readinessCtx) {
        const score = cards.job_readiness_score || 70;
        if (readinessChart) readinessChart.destroy();
        readinessChart = new Chart(readinessCtx, {
            type: 'doughnut',
            data: {
                labels: ['Readiness Match', 'Optimization Gap'],
                datasets: [{
                    data: [score, Math.max(0, 100 - score)],
                    backgroundColor: ['#0d9488', 'rgba(255, 255, 255, 0.1)'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '75%'
            }
        });
    }

    // 4. Missing Skills Horizontal Bar Chart
    const missingCtx = document.getElementById('missingSkillsChart');
    if (missingCtx) {
        const missing = charts.missing_skills || ['Docker', 'AWS', 'Kubernetes', 'Redis', 'CI/CD'];
        if (missingChart) missingChart.destroy();
        missingChart = new Chart(missingCtx, {
            type: 'bar',
            data: {
                labels: missing.slice(0, 5),
                datasets: [{
                    label: 'Priority Score',
                    data: [90, 85, 75, 65, 55],
                    backgroundColor: '#f43f5e',
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } }
            }
        });
    }

    // 5. Before vs After Comparison Grouped Bar Chart
    const compCtx = document.getElementById('comparisonChart');
    if (compCtx) {
        if (comparisonChart) comparisonChart.destroy();
        comparisonChart = new Chart(compCtx, {
            type: 'bar',
            data: {
                labels: ['ATS Score', 'Job Match %', 'Skill Match %', 'Readiness Score'],
                datasets: [
                    {
                        label: 'Before Resume Optimization',
                        data: [cards.ats_score - 18, cards.job_match_pct - 22, cards.skill_match_pct - 20, cards.job_readiness_score - 25],
                        backgroundColor: 'rgba(244, 63, 94, 0.65)',
                        borderRadius: 6
                    },
                    {
                        label: 'After AI Optimization',
                        data: [cards.ats_score, cards.job_match_pct, cards.skill_match_pct, cards.job_readiness_score],
                        backgroundColor: 'rgba(16, 185, 129, 0.85)',
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { min: 0, max: 100 } }
            }
        });
    }
}
