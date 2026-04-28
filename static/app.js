document.addEventListener('DOMContentLoaded', () => {
    // Tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(btn.dataset.target).classList.add('active');
        });
    });

    // Clinical Logic
    let clinicalDataState = {};

    document.getElementById('clinical-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        document.getElementById('clinical-placeholder').classList.add('hidden');
        document.getElementById('clinical-results').classList.add('hidden');
        document.getElementById('clinical-loading').classList.remove('hidden');

        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/api/clinical', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            
            if (response.ok) {
                clinicalDataState = result;
                
                document.getElementById('c-risk-score').textContent = `${result.risk_pct}%`;
                
                // Add a small delay for progress animation to trigger cleanly
                setTimeout(() => {
                    document.getElementById('c-progress').style.width = `${Math.min(result.risk_pct, 100)}%`;
                }, 100);
                
                const badge = document.getElementById('c-badge');
                badge.textContent = `${result.risk_tier} Risk`;
                badge.className = 'risk-badge';
                if (result.risk_tier === 'Low') badge.classList.add('bd-low');
                else if (result.risk_tier === 'Medium') badge.classList.add('bd-med');
                else badge.classList.add('bd-high');

                document.getElementById('c-classification').textContent = result.result_label;

                const factorsList = document.getElementById('c-factors');
                factorsList.innerHTML = '';
                result.factors.forEach(f => {
                    const li = document.createElement('li');
                    li.textContent = f;
                    factorsList.appendChild(li);
                });

                document.getElementById('c-ai-brief').innerHTML = formatAIText(result.suggestion);
                
                const cContactDiv = document.getElementById('c-contact');
                if (result.risk_tier === 'Medium' || result.risk_tier === 'High') {
                    cContactDiv.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg> <div><strong>Urgent: Specialist Consultation Recommended</strong><br>Contact Dr. Jane Smith (Cardiology Dept)<br>Phone: 1-800-555-0199 | Emergency: 911</div>';
                    cContactDiv.classList.remove('hidden');
                    clinicalDataState.contact_info = "Dr. Jane Smith (Cardiology Dept) | Phone: 1-800-555-0199 | Emergency: 911";
                } else {
                    cContactDiv.classList.add('hidden');
                    clinicalDataState.contact_info = "";
                }

                document.getElementById('clinical-loading').classList.add('hidden');
                document.getElementById('clinical-results').classList.remove('hidden');
            } else {
                alert('Error: ' + result.error);
                document.getElementById('clinical-loading').classList.add('hidden');
                document.getElementById('clinical-placeholder').classList.remove('hidden');
            }
        } catch (err) {
            alert('Request failed.');
            document.getElementById('clinical-loading').classList.add('hidden');
            document.getElementById('clinical-placeholder').classList.remove('hidden');
        }
    });

    document.getElementById('c-download').addEventListener('click', () => {
        if (!clinicalDataState.input_snapshot) return;
        downloadReport('Cardio Risk — Clinical', 'Clinical tabular model', clinicalDataState);
    });

    // ECG Logic
    let ecgDataState = {};
    const fileInput = document.getElementById('ecg-file');
    const submitBtn = document.getElementById('ecg-submit-btn');
    const previewContainer = document.getElementById('image-preview-container');
    const previewImg = document.getElementById('image-preview');
    const uploadZone = document.getElementById('upload-zone');

    // Drag and drop styles
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            handleFileSelect(fileInput.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files[0]) handleFileSelect(e.target.files[0]);
    });

    function handleFileSelect(file) {
        submitBtn.disabled = false;
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            previewContainer.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }

    document.getElementById('ecg-reset-btn').addEventListener('click', () => {
        fileInput.value = '';
        submitBtn.disabled = true;
        previewContainer.style.display = 'none';
        document.getElementById('ecg-results').classList.add('hidden');
        document.getElementById('ecg-placeholder').classList.remove('hidden');
    });

    document.getElementById('ecg-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        document.getElementById('ecg-placeholder').classList.add('hidden');
        document.getElementById('ecg-results').classList.add('hidden');
        document.getElementById('ecg-loading').classList.remove('hidden');

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        try {
            const response = await fetch('/api/ecg', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            
            if (response.ok) {
                ecgDataState = result;
                
                document.getElementById('e-class').textContent = result.label;
                document.getElementById('e-conf').textContent = `${(result.confidence * 100).toFixed(1)}%`;
                
                const alertBox = document.getElementById('e-alert');
                alertBox.className = 'alert-box';
                if (['MI', 'Abnormal'].includes(result.label)) {
                    alertBox.classList.add('error');
                    alertBox.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg> <span>This result category may warrant clinical correlation — it is not a diagnosis.</span>';
                } else {
                    alertBox.classList.add('success');
                    alertBox.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg> <span>Model output in a non-urgent category; still not a medical clearance.</span>';
                }

                document.getElementById('e-hr').textContent = result.hr;
                document.getElementById('e-var').textContent = result.var.toFixed(4);

                drawECGChart(result.wave, result.peaks);

                document.getElementById('e-ai-brief').innerHTML = formatAIText(result.suggestion);
                
                const eContactDiv = document.getElementById('e-contact');
                if (['MI', 'Abnormal'].includes(result.label)) {
                    eContactDiv.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg> <div><strong>Urgent: Specialist Consultation Recommended</strong><br>Contact Dr. Jane Smith (Cardiology Dept)<br>Phone: 1-800-555-0199 | Emergency: 911</div>';
                    eContactDiv.classList.remove('hidden');
                    ecgDataState.contact_info = "Dr. Jane Smith (Cardiology Dept) | Phone: 1-800-555-0199 | Emergency: 911";
                } else {
                    eContactDiv.classList.add('hidden');
                    ecgDataState.contact_info = "";
                }

                document.getElementById('ecg-loading').classList.add('hidden');
                document.getElementById('ecg-results').classList.remove('hidden');
            } else {
                alert('Error: ' + result.error);
                document.getElementById('ecg-loading').classList.add('hidden');
                document.getElementById('ecg-placeholder').classList.remove('hidden');
            }
        } catch (err) {
            alert('Request failed.');
            document.getElementById('ecg-loading').classList.add('hidden');
            document.getElementById('ecg-placeholder').classList.remove('hidden');
        }
    });

    document.getElementById('e-download').addEventListener('click', () => {
        if (!ecgDataState.input_snapshot) return;
        downloadReport('Cardio Risk — ECG', 'ECG image CNN + waveform heuristics', ecgDataState);
    });

    async function downloadReport(title, mode, state) {
        try {
            const response = await fetch('/api/report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: title,
                    mode_label: mode,
                    input_snapshot: state.input_snapshot,
                    result_snapshot: state.result_snapshot,
                    suggestion: state.suggestion,
                    contact_info: state.contact_info
                })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `report_${new Date().getTime()}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            } else {
                alert('Failed to generate PDF.');
            }
        } catch (err) {
            alert('Error generating report.');
        }
    }

    function formatAIText(text) {
        if (!text) return "";
        let formatted = text.replace(/(Risk Level:|Explanation:|Actionable Steps:|When to see a doctor:)/g, '<br><strong style="color: var(--primary); font-size: 1.05rem;">$1</strong><br>');
        if (formatted.startsWith('<br>')) formatted = formatted.substring(4);
        formatted = formatted.replace(/\n/g, '<br>');
        return formatted;
    }

    // ── ECG paper-style chart ─────────────────────────────────────────────────
    function drawECGChart(wave, peaks) {
        const canvas = document.getElementById('ecg-waveform-canvas');
        if (!canvas) return;

        // Size canvas to its CSS display size for sharp rendering
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        const W = Math.round(rect.width  || canvas.offsetWidth  || 600);
        const H = Math.round(rect.height || canvas.offsetHeight || 140);
        canvas.width  = W * dpr;
        canvas.height = H * dpr;

        const ctx = canvas.getContext('2d');
        ctx.scale(dpr, dpr);

        // ── Background: dark warm red-tinted ──
        ctx.fillStyle = '#1a0a0a';
        ctx.fillRect(0, 0, W, H);

        // ── ECG paper grid ──
        const smallCell = 8;   // small square (1 mm equivalent)
        const largeCell = smallCell * 5; // large square (5 mm equivalent)

        // Small grid lines
        ctx.strokeStyle = 'rgba(180, 40, 40, 0.22)';
        ctx.lineWidth = 0.5;
        for (let x = 0; x < W; x += smallCell) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
        }
        for (let y = 0; y < H; y += smallCell) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
        }

        // Large grid lines
        ctx.strokeStyle = 'rgba(210, 60, 60, 0.42)';
        ctx.lineWidth = 1;
        for (let x = 0; x < W; x += largeCell) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
        }
        for (let y = 0; y < H; y += largeCell) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
        }

        if (!wave || wave.length < 2) return;

        // ── Map waveform data → canvas coords ──
        const pad = { top: 12, bottom: 12 };
        const plotH = H - pad.top - pad.bottom;
        const n = wave.length;

        function xAt(i) { return (i / (n - 1)) * W; }
        // Flip: signal=1 → top, signal=0 → bottom
        function yAt(v) { return pad.top + (1 - v) * plotH; }

        // ── Waveform glow pass (wider, semi-transparent) ──
        ctx.beginPath();
        ctx.moveTo(xAt(0), yAt(wave[0]));
        for (let i = 1; i < n; i++) ctx.lineTo(xAt(i), yAt(wave[i]));
        ctx.strokeStyle = 'rgba(13, 148, 136, 0.28)';
        ctx.lineWidth = 4;
        ctx.lineJoin = 'round';
        ctx.stroke();

        // ── Waveform main line ──
        ctx.beginPath();
        ctx.moveTo(xAt(0), yAt(wave[0]));
        for (let i = 1; i < n; i++) ctx.lineTo(xAt(i), yAt(wave[i]));
        ctx.strokeStyle = '#0d9488';
        ctx.lineWidth = 1.5;
        ctx.lineJoin = 'round';
        ctx.stroke();

        // ── R-peak markers ──
        if (peaks && peaks.length) {
            peaks.forEach(pi => {
                if (pi < 0 || pi >= n) return;
                const px = xAt(pi);
                const py = yAt(wave[pi]);

                // Outer halo
                const halo = ctx.createRadialGradient(px, py, 1, px, py, 7);
                halo.addColorStop(0, 'rgba(30, 58, 95, 0.9)');
                halo.addColorStop(1, 'rgba(30, 58, 95, 0)');
                ctx.beginPath();
                ctx.arc(px, py, 7, 0, Math.PI * 2);
                ctx.fillStyle = halo;
                ctx.fill();

                // Dot
                ctx.beginPath();
                ctx.arc(px, py, 3, 0, Math.PI * 2);
                ctx.fillStyle = '#1e3a5f';
                ctx.fill();
                ctx.strokeStyle = 'rgba(96,165,250,0.7)';
                ctx.lineWidth = 1;
                ctx.stroke();
            });
        }

        // ── Baseline label ──
        ctx.font = '9px monospace';
        ctx.fillStyle = 'rgba(180,60,60,0.5)';
        ctx.fillText('Norm. signal', 6, H - 4);
    }
    // ─────────────────────────────────────────────────────────────────────────
});
