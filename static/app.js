const uploadArea = document.getElementById('uploadArea');
const imageInput = document.getElementById('imageInput');
const previewImage = document.getElementById('previewImage');
const extractBtn = document.getElementById('extractBtn');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const results = document.getElementById('results');
const emptyState = document.getElementById('emptyState');
const colorsGrid = document.getElementById('colorsGrid');
const stats = document.getElementById('stats');
const paletteDescription = document.getElementById('paletteDescription');
const apiEndpoint = document.getElementById('apiEndpoint');

let selectedFile = null;
let projectId = 1; // Default project ID (will create if needed)

// Upload area click handler
uploadArea.addEventListener('click', () => imageInput.click());

// File input change handler
imageInput.addEventListener('change', handleFileSelect);

// Drag and drop handlers
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
    };
    reader.readAsDataURL(selectedFile);
}

extractBtn.addEventListener('click', extractColors);

async function extractColors() {
    if (!selectedFile) return;

    extractBtn.disabled = true;
    loading.style.display = 'block';
    results.style.display = 'none';
    emptyState.style.display = 'none';
    error.classList.remove('show');

    try {
        // Ensure project exists
        await ensureProject();

        // Upload image to temporary storage or use URL
        const formData = new FormData();
        formData.append('file', selectedFile);

        // For this demo, we'll convert to data URL
        const reader = new FileReader();
        reader.onload = async (e) => {
            const base64Image = e.target.result;
            await callExtractAPI(base64Image);
        };
        reader.readAsDataURL(selectedFile);
    } catch (err) {
        showError(`Error: ${err.message}`);
        extractBtn.disabled = false;
        loading.style.display = 'none';
    }
}

async function ensureProject() {
    try {
        const response = await fetch(`/api/v1/projects/${projectId}/colors`);
        if (response.status === 404) {
            // Create a new project
            const createResponse = await fetch('/api/v1/projects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: 'Demo Project', description: 'Educational demo' })
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
        apiEndpoint.textContent = `POST ${endpoint}`;
        apiEndpoint.style.display = 'block';

        // Call backend API with base64 image
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image_base64: base64Image,
                project_id: projectId,
                max_colors: 8
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            showError(`Extraction failed: ${errorData.detail || 'Unknown error'}`);
            return;
        }

        const result = await response.json();
        showResults(result);
    } catch (err) {
        showError(`API Error: ${err.message}`);
    } finally {
        extractBtn.disabled = false;
        loading.style.display = 'none';
    }
}


function showResults(result) {
    const colorsData = result.colors || [];
    const avgConfidence = colorsData.length > 0
        ? (colorsData.reduce((a, c) => a + c.confidence, 0) / colorsData.length * 100).toFixed(0)
        : 0;
    const extractorUsed = result.extractor_used || 'unknown';

    // Update stats
    stats.innerHTML = `
        <div class="stat">
            <div class="stat-value">${colorsData.length}</div>
            <div class="stat-label">Colors Extracted</div>
        </div>
        <div class="stat">
            <div class="stat-value">${avgConfidence}%</div>
            <div class="stat-label">Avg Confidence</div>
        </div>
        <div class="stat">
            <div class="stat-value">${extractorUsed}</div>
            <div class="stat-label">AI Model</div>
        </div>
    `;

    // Update palette description
    const paletteDesc = result.color_palette || 'Color palette extracted from your image.';
    paletteDescription.textContent = `🎨 ${paletteDesc}`;

    // Update colors grid
    colorsGrid.innerHTML = colorsData.map(color => `
        <div class="color-card">
            <div class="color-swatch" style="background-color: ${color.hex};">
                ${isLightColor(color.hex) ? '🎯' : ''}
            </div>
            <div class="color-info">
                <div class="color-name">${color.name}</div>
                ${color.semantic_name ? `<div class="color-semantic">${color.semantic_name}</div>` : ''}
                <div class="color-hex">${color.hex}</div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${color.confidence * 100}%"></div>
                </div>
            </div>
        </div>
    `).join('');

    results.style.display = 'block';
    emptyState.style.display = 'none';
}

function isLightColor(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    const brightness = (r * 299 + g * 587 + b * 114) / 1000;
    return brightness > 128;
}

function showError(message) {
    error.textContent = message;
    error.classList.add('show');
}
