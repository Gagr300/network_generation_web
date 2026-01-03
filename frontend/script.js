// Глобальные переменные
let socket = null;
let currentSessionId = null;
let currentGraphData = null;
let currentMetrics = null;
let progressInterval = null;
let totalEdgesToGenerate = 0;
let currentGeneratedEdges = 0;

// Инициализация drag and drop
document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');

    // Обработка drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        uploadArea.style.borderColor = '#4a5568';
        uploadArea.style.background = '#edf2f7';
    }

    function unhighlight() {
        uploadArea.style.borderColor = '#cbd5e0';
        uploadArea.style.background = '#f7fafc';
    }

    uploadArea.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFileSelect, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFileSelect(e) {
        handleFiles(e.target.files);
    }
});

// Обработка загруженных файлов
async function handleFiles(files) {
    if (files.length === 0) return;

    const file = files[0];
    const formData = new FormData();
    formData.append('file', file);

    showLoading('Uploading and analyzing graph...');

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            currentGraphData = data.graph;
            currentMetrics = data.metrics;
            displayCombinedMetrics(data.metrics, data.graph);
            enableButtons();
            showSuccess('Graph uploaded successfully!');
        } else {
            throw new Error(data.error || 'Upload failed');
        }
    } catch (error) {
        showError('Error uploading graph: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Загрузка примера данных
async function loadSampleData() {
    showLoading('Loading sample dataset...');

    try {
        const response = await fetch('/api/sample', {
            method: 'GET'
        });

        const data = await response.json();

        if (data.success) {
            currentGraphData = data.graph;
            currentMetrics = data.metrics;
            displayCombinedMetrics(data.metrics, data.graph);
            enableButtons();
            showSuccess('Sample dataset loaded successfully!');
        } else {
            throw new Error(data.error || 'Failed to load sample');
        }
    } catch (error) {
        showError('Error loading sample: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Анализ мотивов
async function analyzeGraph() {
    if (!currentGraphData) return;

    showLoading('Analyzing triplet motifs...');

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                graph: currentGraphData
            })
        });

        const data = await response.json();

        if (data.success) {
            displayMotifAnalysis(data);
            showSuccess('Motif analysis completed!');
        } else {
            throw new Error(data.error || 'Analysis failed');
        }
    } catch (error) {
        showError('Error analyzing motifs: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Генерация нового графа
async function generateGraph() {
    if (!currentGraphData) return;

    // Генерируем уникальный ID сессии
    currentSessionId = Date.now().toString();

    const totalEdges = currentGraphData.edges.length;

    // Показываем прогресс-бар
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.style.display = 'block';
        document.getElementById('progressFill').style.width = '0%';
        document.getElementById('progressPercentage').textContent = '0%';
        document.getElementById('progressText').textContent = '0 / ' + totalEdges;
        document.getElementById('progressDetails').textContent = 'Starting generation...';
    }

    // Отключаем кнопку генерации во время процесса
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    }

    try {
        const response = await fetch('/api/generate_stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                original_graph: currentGraphData,
                session_id: currentSessionId
            })
        });

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Failed to start generation');
        }

        console.log('Generation started with session:', data.session_id);

        // Запускаем polling для проверки прогресса
        startProgressPolling();

        // Также запускаем обычную генерацию для совместимости
        generateLegacy();

    } catch (error) {
        showError('Error starting generation: ' + error.message);
        resetGenerateButton();
        document.getElementById('progressContainer').style.display = 'none';
    }
}

async function generateLegacy() {
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                original_graph: currentGraphData
            })
        });

        const data = await response.json();

        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }

        if (data.success) {
            // Показываем 100%
            updateProgressDisplay(100, currentGraphData.edges.length, currentGraphData.edges.length);
            document.getElementById('progressDetails').textContent = 'Generation complete!';

            // Обновляем данные
            currentGraphData = data.graph;
            currentMetrics = data.metrics;
            displayCombinedMetrics(data.metrics, data.graph);

            showSuccess('New graph generated successfully!');

            // Скрываем прогресс-бар через 2 секунды
            setTimeout(() => {
                const progressContainer = document.getElementById('progressContainer');
                if (progressContainer) {
                    progressContainer.style.display = 'none';
                }
            }, 2000);
        } else {
            throw new Error(data.error || 'Generation failed');
        }
    } catch (error) {
        showError('Error generating graph: ' + error.message);
        document.getElementById('progressDetails').textContent = 'Error: ' + error.message;
    } finally {
        resetGenerateButton();
        currentSessionId = null;
    }
}

// Скачивание edgelist в формате .txt
async function downloadTxt() {
    if (!currentGraphData) return;

    showLoading('Preparing edgelist download...');

    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                graph: currentGraphData,
                format: 'txt'
            })
        });

        if (!response.ok) {
            throw new Error('Download failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `graph_edgelist_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showSuccess('Edgelist download started!');
    } catch (error) {
        showError('Error downloading: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Скачивание всей информации в формате JSON
async function downloadJson() {
    if (!currentGraphData || !currentMetrics) return;

    showLoading('Preparing JSON download...');

    try {
        // Получаем анализ мотивов
        let motifAnalysis = null;
        try {
            const analysisResponse = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    graph: currentGraphData
                })
            });

            if (analysisResponse.ok) {
                motifAnalysis = await analysisResponse.json();
            }
        } catch (error) {
            console.warn('Could not get motif analysis for JSON:', error);
        }

        // Создаем полный объект с данными
        const fullData = {
            graph: currentGraphData,
            metrics: currentMetrics,
            motifAnalysis: motifAnalysis?.success ? motifAnalysis : null,
            metadata: {
                generatedAt: new Date().toISOString(),
                nodesCount: currentGraphData.nodes.length,
                edgesCount: currentGraphData.edges.length,
                fileName: `graph_complete_${new Date().toISOString().split('T')[0]}.json`
            }
        };

        // Создаем и скачиваем JSON файл
        const dataStr = JSON.stringify(fullData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = window.URL.createObjectURL(dataBlob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fullData.metadata.fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showSuccess('Complete information download started!');
    } catch (error) {
        showError('Error downloading JSON: ' + error.message);
    } finally {
        hideLoading();
    }
}

function startProgressPolling() {
    if (progressInterval) {
        clearInterval(progressInterval);
    }

    progressInterval = setInterval(async () => {
        if (!currentSessionId) return;

        try {
            // Здесь можно добавить endpoint для получения прогресса
            // Но для простоты будем использовать эмуляцию прогресса
            updateProgressSimulation();
        } catch (error) {
            console.error('Error checking progress:', error);
        }
    }, 500);
}

// Управление прогресс-баром
function startProgressTracking(totalEdges) {
    // Эта функция теперь не нужна для WebSocket версии,
    // но оставляем для совместимости с legacy кодом
    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.style.display = 'block';
        document.getElementById('progressFill').style.width = '0%';
        document.getElementById('progressPercentage').textContent = '0%';
        document.getElementById('progressText').textContent = '0 / ' + totalEdges;
    }
}

function updateProgressSimulation() {
    const progressContainer = document.getElementById('progressContainer');
    if (!progressContainer || progressContainer.style.display === 'none') return;

    const currentProgress = parseInt(document.getElementById('progressFill').style.width) || 0;
    const totalEdges = currentGraphData.edges.length;

    if (currentProgress < 95) {
        // Имитация прогресса
        const increment = Math.floor(Math.random() * 5);
        const newProgress = Math.min(95, currentProgress + increment);
        const currentEdges = Math.floor((newProgress / 100) * totalEdges);

        updateProgressDisplay(newProgress, currentEdges, totalEdges);
        document.getElementById('progressDetails').textContent =
            `Generating edges: ${currentEdges} / ${totalEdges}`;
    }
}

function updateProgressDisplay(percentage, current, total) {
    const progressFill = document.getElementById('progressFill');
    const progressPercentage = document.getElementById('progressPercentage');
    const progressText = document.getElementById('progressText');

    if (progressFill && progressPercentage && progressText) {
        progressFill.style.width = percentage + '%';
        progressPercentage.textContent = percentage + '%';
        progressText.textContent = current + ' / ' + total;
        progressFill.style.transition = 'width 0.3s ease';
    }
}


function completeProgress() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
    updateProgressDisplay(100);

    // Скрываем прогресс-бар через 2 секунды
    setTimeout(() => {
        const progressContainer = document.getElementById('progressContainer');
        if (progressContainer) {
            progressContainer.style.display = 'none';
        }
    }, 2000);
}

// Отображение объединенных метрик и информации
function displayCombinedMetrics(metrics, graphData) {
    const metricsDiv = document.getElementById('combinedMetrics');

    if (!metrics || !graphData) {
        metricsDiv.innerHTML = `
            <div class="metrics-placeholder">
                <i class="fas fa-chart-network fa-3x"></i>
                <p>No graph data available</p>
            </div>
        `;
        return;
    }

    // Сохраняем метрики для скачивания JSON
    currentMetrics = metrics;

    // Базовые метрики
    const nodeCount = metrics.num_nodes || graphData.nodes.length;
    const edgeCount = metrics.num_edges || graphData.edges.length;
    const density = metrics.density || (nodeCount > 1 ? (edgeCount / (nodeCount * (nodeCount - 1))).toFixed(4) : '0.0000');

    // Форматируем значения
    const formatValue = (value, decimalPlaces = 2) => {
        if (value === undefined || value === null) return 'N/A';
        if (typeof value === 'number') {
            return value.toFixed(decimalPlaces);
        }
        return value;
    };

    metricsDiv.innerHTML = `
        <div class="combined-metrics-container">
            <!-- Основные метрики -->
            <div class="metrics-section">
                <h3><i class="fas fa-ruler-combined"></i> Basic Metrics</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-circle-nodes"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${nodeCount}</div>
                            <div class="metric-label">Number of Vertices</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-link"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${edgeCount}</div>
                            <div class="metric-label">Number of Arcs</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-project-diagram"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${formatValue(density, 4)}</div>
                            <div class="metric-label">Graph Density</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Связность -->
            <div class="metrics-section">
                <h3><i class="fas fa-sitemap"></i> Connectivity</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-unlink"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${metrics.weakly_connected || 'N/A'}</div>
                            <div class="metric-label">Weakly Connected</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-link"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${metrics.strongly_connected || 'N/A'}</div>
                            <div class="metric-label">Strongly Connected</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-expand"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${metrics.strongly_connected_nodes || metrics.num_nodes || nodeCount}</div>
                            <div class="metric-label">Vertices in Largest SCC</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Статистики графа -->
            <div class="metrics-section">
                <h3><i class="fas fa-chart-line"></i> Graph Statistics</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-exchange-alt"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${formatValue(metrics.transitivity, 3)}</div>
                            <div class="metric-label">Transitivity</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-retweet"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${formatValue(metrics.reciprocity, 3)}</div>
                            <div class="metric-label">Reciprocity</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-snowflake"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${formatValue(metrics.avg_clustering, 3)}</div>
                            <div class="metric-label">Avg Clustering</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Степени вершин -->
            <div class="metrics-section">
                <h3><i class="fas fa-signal"></i> Degree Statistics</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-signal"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${formatValue(metrics.avg_in_degree)}</div>
                            <div class="metric-label">Avg In-Degree</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-signal"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${formatValue(metrics.avg_out_degree)}</div>
                            <div class="metric-label">Avg Out-Degree</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-chart-bar"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${metrics.max_in_degree || 'N/A'}</div>
                            <div class="metric-label">Max In-Degree</div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon">
                            <i class="fas fa-chart-bar"></i>
                        </div>
                        <div class="metric-content">
                            <div class="metric-value">${metrics.max_out_degree || 'N/A'}</div>
                            <div class="metric-label">Max Out-Degree</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Вспомогательные функции
function countSelfLoops(graphData) {
    if (!graphData || !graphData.edges) return 0;
    return graphData.edges.filter(edge => edge.source === edge.target).length;
}

function countReciprocalEdges(graphData) {
    if (!graphData || !graphData.edges) return 0;

    const edgeSet = new Set();
    let reciprocalCount = 0;

    graphData.edges.forEach(edge => {
        const edgeKey = `${edge.source}-${edge.target}`;
        const reverseKey = `${edge.target}-${edge.source}`;

        if (edgeSet.has(reverseKey)) {
            reciprocalCount++;
        }
        edgeSet.add(edgeKey);
    });

    return reciprocalCount;
}

// Инициализация WebSocket при загрузке страницы
function initializeWebSocket() {
    if (!socket) {
        // Подключаемся к WebSocket серверу
        socket = io('http://' + window.location.hostname + ':5000');

        socket.on('connect', function() {
            console.log('Connected to WebSocket server');
        });

        socket.on('generation_progress', function(data) {
            if (data.session_id === currentSessionId) {
                updateProgressDisplay(data.progress, data.current, data.total);
            }
        });

        socket.on('generation_complete', function(data) {
            if (data.session_id === currentSessionId) {
                handleGenerationComplete(data);
            }
        });

        socket.on('generation_error', function(data) {
            if (data.session_id === currentSessionId) {
                handleGenerationError(data);
            }
        });

        socket.on('disconnect', function() {
            console.log('Disconnected from WebSocket server');
        });
    }
}

// Отображение анализа мотивов
function displayMotifAnalysis(data) {
    const analysisDiv = document.getElementById('motifAnalysis');

    if (!data.motifs || data.motifs.length === 0) {
        analysisDiv.innerHTML = `
            <div class="analysis-placeholder">
                <i class="fas fa-chart-pie fa-3x"></i>
                <p>No motif data available</p>
            </div>
        `;
        return;
    }

    // Сортируем мотивы по количеству
    const sortedMotifs = [...data.motifs].sort((a, b) => b.count - a.count);

    let html = `
        <div class="motif-summary">
            <div class="summary-card">
                <h3>${data.total_motifs}</h3>
                <p>Total Triplets</p>
            </div>
        </div>
        <div class="motif-table-container">
            <h4>Motif Distribution</h4>
            <table class="motif-table">
                <thead>
                    <tr>
                        <th>Motif ID</th>
                        <th>Count</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
    `;

    sortedMotifs.forEach(motif => {
        const percentage = data.total_motifs > 0 ? ((motif.count / data.total_motifs) * 100).toFixed(2) : '0.00';
        html += `
            <tr>
                <td><strong>M${motif.id}</strong></td>
                <td>${motif.count}</td>
                <td>${percentage}%</td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
        <div class="motif-insights">
            <h4>Insights:</h4>
            <ul>
                <li><strong>Most common motif:</strong> M${sortedMotifs[0].id} (${((sortedMotifs[0].count / data.total_motifs) * 100).toFixed(2)}%)</li>
                <li><strong>Least common motif:</strong> M${sortedMotifs[sortedMotifs.length - 1].id} (${((sortedMotifs[sortedMotifs.length - 1].count / data.total_motifs) * 100).toFixed(2)}%)</li>
                <li><strong>Number of unique motifs:</strong> ${sortedMotifs.filter(m => m.count > 0).length}</li>
            </ul>
        </div>
    `;

    analysisDiv.innerHTML = html;
}

// Обработка завершения генерации
function handleGenerationComplete(data) {
    if (data.success) {
        currentGraphData = data.graph;
        currentMetrics = data.metrics;
        displayCombinedMetrics(data.metrics, data.graph);

        // Показываем 100% на несколько секунд
        setTimeout(() => {
            const progressContainer = document.getElementById('progressContainer');
            if (progressContainer) {
                progressContainer.style.display = 'none';
            }
        }, 2000);

        showSuccess('New graph generated successfully!');
    }

    resetGenerateButton();
    currentSessionId = null;
}

// Обработка ошибки генерации
function handleGenerationError(data) {
    showError('Error generating graph: ' + data.error);
    resetGenerateButton();

    const progressContainer = document.getElementById('progressContainer');
    if (progressContainer) {
        progressContainer.style.display = 'none';
    }

    currentSessionId = null;
}

// Сброс кнопки генерации
function resetGenerateButton() {
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate New Graph';
    }
}



// Включение кнопок
function enableButtons() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const generateBtn = document.getElementById('generateBtn');
    const downloadTxtBtn = document.getElementById('downloadTxtBtn');
    const downloadJsonBtn = document.getElementById('downloadJsonBtn');

    if (analyzeBtn) analyzeBtn.disabled = false;
    if (generateBtn) generateBtn.disabled = false;
    if (downloadTxtBtn) downloadTxtBtn.disabled = false;
    if (downloadJsonBtn) downloadJsonBtn.disabled = false;
}

// Управление загрузкой
function showLoading(message) {
    const loadingMessage = document.getElementById('loadingMessage');
    const loadingModal = document.getElementById('loadingModal');

    if (loadingMessage) loadingMessage.textContent = message;
    if (loadingModal) loadingModal.classList.add('active');
}

function hideLoading() {
    const loadingModal = document.getElementById('loadingModal');
    if (loadingModal) loadingModal.classList.remove('active');
}

function showSuccess(message) {
    console.log('Success:', message);
    // Можно добавить уведомление в интерфейс
}

function showError(message) {
    console.error('Error:', message);
    alert('Error: ' + message);
}