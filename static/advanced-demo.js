// Advanced Pipeline Demo - JavaScript
// Visualizes the full 5-stage color extraction pipeline

const uploadArea = document.getElementById('uploadArea');
const imageInput = document.getElementById('imageInput');
const previewImage = document.getElementById('previewImage');
const extractBtn = document.getElementById('extractBtn');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const results = document.getElementById('results');
const emptyState = document.getElementById('emptyState');
const colorsGrid = document.getElementById('colorsGrid');
const colorsCard = document.getElementById('colorsCard');
const stats = document.getElementById('stats');
const paletteDescription = document.getElementById('paletteDescription');
const colorDetail = document.getElementById('colorDetail');

let selectedFile = null;
let projectId = 1;
let currentColors = [];
let selectedColorIndex = null;

// Pipeline stages for visualization
const stages = ['preprocess', 'extract', 'aggregate', 'validate', 'generate'];

// Upload handlers
uploadArea.addEventListener('click', () => imageInput.click());
imageInput.addEventListener('change', handleFileSelect);

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
});

function handleFileSelect(e) {
    handleFiles(e.target.files);
}

function handleFiles(files) {
    if (files.length === 0) return;

    selectedFile = files[0];
    if (!selectedFile.type.startsWith('image/')) {
        showError('Please select an image file');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewImage.style.display = 'block';
        extractBtn.style.display = 'block';
        error.classList.remove('show');
        resetPipelineStages();
    };
    reader.readAsDataURL(selectedFile);
}

extractBtn.addEventListener('click', extractColors);

function resetPipelineStages() {
    stages.forEach(stage => {
        const stageEl = document.getElementById(`stage-${stage}`);
        const statusEl = document.getElementById(`status-${stage}`);
        stageEl.classList.remove('active', 'complete', 'error');
        statusEl.textContent = 'Pending';
        statusEl.className = 'stage-status pending';
    });
}

function updateStage(stage, status) {
    const stageEl = document.getElementById(`stage-${stage}`);
    const statusEl = document.getElementById(`status-${stage}`);

    stageEl.classList.remove('active', 'complete', 'error');

    switch(status) {
        case 'running':
            stageEl.classList.add('active');
            statusEl.textContent = 'Running...';
            statusEl.className = 'stage-status running';
            break;
        case 'done':
            stageEl.classList.add('complete');
            statusEl.textContent = 'Done';
            statusEl.className = 'stage-status done';
            break;
        case 'error':
            stageEl.classList.add('error');
            statusEl.textContent = 'Error';
            statusEl.className = 'stage-status error';
            break;
    }
}

async function extractColors() {
    if (!selectedFile) return;

    extractBtn.disabled = true;
    loading.classList.add('show');
    results.style.display = 'none';
    emptyState.style.display = 'none';
    colorsCard.style.display = 'none';
    error.classList.remove('show');
    colorDetail.classList.remove('visible');

    resetPipelineStages();

    try {
        await ensureProject();

        // Simulate pipeline stages with actual extraction
        // Stage 1: Preprocess
        updateStage('preprocess', 'running');
        await delay(300);
        updateStage('preprocess', 'done');

        // Stage 2: Extract
        updateStage('extract', 'running');

        const reader = new FileReader();
        reader.onload = async (e) => {
            const base64Image = e.target.result;
            await callExtractAPI(base64Image);
        };
        reader.readAsDataURL(selectedFile);

    } catch (err) {
        showError(`Error: ${err.message}`);
        extractBtn.disabled = false;
        loading.classList.remove('show');
    }
}

async function ensureProject() {
    try {
        const response = await fetch(`/api/v1/projects/${projectId}/colors`);
        if (response.status === 404) {
            const createResponse = await fetch('/api/v1/projects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: 'Advanced Demo Project', description: 'Pipeline visualization demo' })
            });
            if (createResponse.ok) {
                const project = await createResponse.json();
                projectId = project.id;
            }
        }
    } catch (err) {
        console.log('Using default project');
    }
}

async function callExtractAPI(base64Image) {
    try {
        const endpoint = `/api/v1/colors/extract`;

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image_base64: base64Image,
                project_id: projectId,
                max_colors: 10
            })
        });

        // Complete extraction stage
        updateStage('extract', 'done');

        if (!response.ok) {
            const errorData = await response.json();
            updateStage('aggregate', 'error');
            showError(`Extraction failed: ${errorData.detail || 'Unknown error'}`);
            return;
        }

        // Stage 3: Aggregate
        updateStage('aggregate', 'running');
        await delay(200);
        updateStage('aggregate', 'done');

        // Stage 4: Validate
        updateStage('validate', 'running');
        await delay(200);
        updateStage('validate', 'done');

        // Stage 5: Generate
        updateStage('generate', 'running');
        await delay(150);
        updateStage('generate', 'done');

        const result = await response.json();
        showResults(result);

    } catch (err) {
        showError(`API Error: ${err.message}`);
    } finally {
        extractBtn.disabled = false;
        loading.classList.remove('show');
    }
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function showResults(result) {
    currentColors = result.colors || [];
    const avgConfidence = currentColors.length > 0
        ? (currentColors.reduce((a, c) => a + c.confidence, 0) / currentColors.length * 100).toFixed(0)
        : 0;
    const extractorUsed = result.extractor_used || 'claude';

    // Count WCAG compliant colors
    const wcagCompliant = currentColors.filter(c => c.wcag_aa_compliant_text).length;

    // Update stats
    stats.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${currentColors.length}</div>
            <div class="stat-label">Colors</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${avgConfidence}%</div>
            <div class="stat-label">Confidence</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${wcagCompliant}</div>
            <div class="stat-label">WCAG AA</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${extractorUsed}</div>
            <div class="stat-label">Extractor</div>
        </div>
    `;

    // Update palette description
    const paletteDesc = result.color_palette || 'Color palette extracted and validated through the pipeline.';
    paletteDescription.textContent = paletteDesc;

    // Update colors grid
    colorsGrid.innerHTML = currentColors.map((color, index) => {
        const tags = [];
        if (color.harmony) tags.push(`<span class="color-tag harmony">${color.harmony}</span>`);
        if (color.temperature) tags.push(`<span class="color-tag temperature">${color.temperature}</span>`);
        if (color.wcag_aa_compliant_text !== undefined) {
            tags.push(`<span class="color-tag ${color.wcag_aa_compliant_text ? 'wcag-pass' : 'wcag-fail'}">
                WCAG ${color.wcag_aa_compliant_text ? 'AA' : 'Fail'}
            </span>`);
        }

        return `
            <div class="color-card" data-index="${index}" onclick="selectColor(${index})">
                <div class="color-swatch" style="background-color: ${color.hex};" onclick="event.stopPropagation(); copyToClipboard('${color.hex}')" title="Click to copy ${color.hex}">
                    <span class="copy-hint">Copy</span>
                </div>
                <div class="color-info">
                    <div class="color-header">
                        <div class="color-name">${color.name}</div>
                        <div class="color-confidence">${(color.confidence * 100).toFixed(0)}%</div>
                    </div>
                    <div class="color-values">${color.hex}</div>
                    <div class="color-tags">${tags.join('')}</div>
                </div>
            </div>
        `;
    }).join('');

    results.style.display = 'block';
    colorsCard.style.display = 'block';
    emptyState.style.display = 'none';

    // Auto-select first color
    if (currentColors.length > 0) {
        selectColor(0);
    }
}

function selectColor(index) {
    selectedColorIndex = index;
    const color = currentColors[index];

    // Update selection state in grid
    document.querySelectorAll('.color-card').forEach((card, i) => {
        card.classList.toggle('selected', i === index);
    });

    // Show detail panel
    colorDetail.classList.add('visible');

    // Update detail swatch
    document.getElementById('detailSwatch').style.backgroundColor = color.hex;

    // Color values
    document.getElementById('detailHex').textContent = color.hex;
    document.getElementById('detailRgb').textContent = color.rgb || '-';
    document.getElementById('detailHsl').textContent = color.hsl || '-';
    document.getElementById('detailHsv').textContent = color.hsv || '-';

    // Properties
    document.getElementById('detailTemp').textContent = color.temperature || '-';
    document.getElementById('detailSat').textContent = color.saturation_level || '-';
    document.getElementById('detailLight').textContent = color.lightness_level || '-';
    document.getElementById('detailHarmony').textContent = color.harmony || '-';

    // WCAG
    const wcagWhite = color.wcag_contrast_on_white;
    const wcagBlack = color.wcag_contrast_on_black;

    const wcagWhiteEl = document.getElementById('wcagWhite');
    wcagWhiteEl.textContent = wcagWhite ? `${wcagWhite.toFixed(2)}:1` : '-';
    wcagWhiteEl.className = `wcag-ratio ${wcagWhite >= 4.5 ? 'pass' : 'fail'}`;

    const wcagBlackEl = document.getElementById('wcagBlack');
    wcagBlackEl.textContent = wcagBlack ? `${wcagBlack.toFixed(2)}:1` : '-';
    wcagBlackEl.className = `wcag-ratio ${wcagBlack >= 4.5 ? 'pass' : 'fail'}`;

    // WCAG compliance badges
    const wcagWhiteComp = document.getElementById('wcagWhiteCompliance');
    const wcagBlackComp = document.getElementById('wcagBlackCompliance');

    wcagWhiteComp.innerHTML = wcagWhite ? `
        <span class="compliance-badge ${wcagWhite >= 4.5 ? 'pass' : 'fail'}">AA ${wcagWhite >= 4.5 ? 'Pass' : 'Fail'}</span>
        <span class="compliance-badge ${wcagWhite >= 7 ? 'pass' : 'fail'}">AAA ${wcagWhite >= 7 ? 'Pass' : 'Fail'}</span>
    ` : '';

    wcagBlackComp.innerHTML = wcagBlack ? `
        <span class="compliance-badge ${wcagBlack >= 4.5 ? 'pass' : 'fail'}">AA ${wcagBlack >= 4.5 ? 'Pass' : 'Fail'}</span>
        <span class="compliance-badge ${wcagBlack >= 7 ? 'pass' : 'fail'}">AAA ${wcagBlack >= 7 ? 'Pass' : 'Fail'}</span>
    ` : '';

    // Variants
    document.getElementById('variantTint').style.backgroundColor = color.tint_color || lightenColor(color.hex);
    document.getElementById('variantBase').style.backgroundColor = color.hex;
    document.getElementById('variantShade').style.backgroundColor = color.shade_color || darkenColor(color.hex);

    // Provenance (if available)
    const provenanceSection = document.getElementById('provenanceSection');
    const provenanceList = document.getElementById('provenanceList');

    if (color.provenance && Object.keys(color.provenance).length > 0) {
        provenanceSection.style.display = 'block';
        provenanceList.innerHTML = Object.entries(color.provenance).map(([source, conf]) => `
            <div class="provenance-item">
                <span class="provenance-source">${source}</span>
                <span class="provenance-confidence">${(conf * 100).toFixed(0)}%</span>
            </div>
        `).join('');
    } else {
        provenanceSection.style.display = 'none';
    }
}

function lightenColor(hex) {
    // Simple lightening function
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);

    const newR = Math.min(255, r + (255 - r) * 0.3);
    const newG = Math.min(255, g + (255 - g) * 0.3);
    const newB = Math.min(255, b + (255 - b) * 0.3);

    return `#${Math.round(newR).toString(16).padStart(2, '0')}${Math.round(newG).toString(16).padStart(2, '0')}${Math.round(newB).toString(16).padStart(2, '0')}`;
}

function darkenColor(hex) {
    // Simple darkening function
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);

    const newR = r * 0.7;
    const newG = g * 0.7;
    const newB = b * 0.7;

    return `#${Math.round(newR).toString(16).padStart(2, '0')}${Math.round(newG).toString(16).padStart(2, '0')}${Math.round(newB).toString(16).padStart(2, '0')}`;
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        const notification = document.createElement('div');
        notification.className = 'copy-notification';
        notification.textContent = `Copied ${text}`;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

function showError(message) {
    error.textContent = message;
    error.classList.add('show');
}

// Make selectColor available globally
window.selectColor = selectColor;
window.copyToClipboard = copyToClipboard;
