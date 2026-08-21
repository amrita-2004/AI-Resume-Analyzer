document.addEventListener('DOMContentLoaded', () => {
    // Initialize Socket.IO connection
    let socket;
    try {
        socket = io();
    } catch (e) {
        console.warn("[WebSocket] Socket.IO client library not loaded or disconnected:", e);
    }

    const uploadForm = document.getElementById('upload-form');
    const progressModal = document.getElementById('progressModal');
    const progressBar = document.getElementById('wsProgressBar');
    const progressMessage = document.getElementById('wsProgressMessage');
    const progressPctText = document.getElementById('wsProgressPct');

    if (uploadForm) {
        uploadForm.addEventListener('submit', () => {
            if (progressModal) {
                progressModal.style.display = 'flex';
            }
            updateProgressState(10, "10% Resume Uploaded & Validated...");
        });
    }

    if (socket) {
        socket.on('connect', () => {
            console.log("[WebSocket] Connected to AI Career Intelligence real-time stream.");
        });

        socket.on('analysis_progress', (data) => {
            console.log("[WebSocket Event]", data);
            if (data) {
                const pct = data.percentage || 10;
                const msg = data.message || "Processing...";
                updateProgressState(pct, msg);

                if (pct >= 100) {
                    setTimeout(() => {
                        if (progressModal) {
                            progressModal.style.display = 'none';
                        }
                    }, 1200);
                }
            }
        });
    }

    function updateProgressState(pct, message) {
        if (progressBar) progressBar.style.width = `${pct}%`;
        if (progressMessage) progressMessage.textContent = message;
        if (progressPctText) progressPctText.textContent = `${pct}%`;

        // Highlight active step item
        const steps = [10, 30, 50, 70, 90, 100];
        steps.forEach(step => {
            const stepEl = document.getElementById(`step-${step}`);
            if (stepEl) {
                if (pct >= step) {
                    stepEl.classList.add('active');
                    stepEl.querySelector('i').className = 'fa-solid fa-check-circle text-teal';
                } else {
                    stepEl.classList.remove('active');
                    stepEl.querySelector('i').className = 'fa-solid fa-circle';
                }
            }
        });
    }
});
