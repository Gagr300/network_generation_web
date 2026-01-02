// Глобальные переменные
let currentGraph = null;
let currentGraphData = null;
let simulation = null;
let showLabels = true;

// Инициализация drag and drop
document.addEventListener('DOMContentLoaded', function() {
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
        uploadArea.style.borderColor = '#667eea';
        uploadArea.style.background = '#e2e8f0';
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
            displayMetrics(data.metrics);
            visualizeGraph(data.graph);
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
        // В реальном приложении здесь был бы запрос к серверу для загрузки примера
        // Для демо создадим простой граф
        const sampleGraph = {
            nodes: Array.from({length: 20}, (_, i) => ({id: `Node${i}`})),
            edges: Array.from({length: 50}, () => ({
                source: `Node${Math.floor(Math.random() * 20)}`,
                target: `Node${Math.floor(Math.random() * 20)}`
            })).filter(edge => edge.source !== edge.target)
        };

        // Создаем пример метрик
        const sampleMetrics = {
            num_nodes: 20,
            num_edges: sampleGraph.edges.length,
            density: (sampleGraph.edges.length / (20 * 19)).toFixed(4),
            avg_in_degree: (sampleGraph.edges.length / 20).toFixed(2),
            avg_out_degree: (sampleGraph.edges.length / 20).toFixed(2),
            max_in_degree: 5,
            max_out_degree: 5,
            strongly_connected_nodes: 15,
            transitivity: 0.3,
            reciprocity: 0.4,
            avg_clustering: 0.25
        };

        currentGraphData = sampleGraph;
        displayMetrics(sampleMetrics);
        visualizeGraph(sampleGraph);
        enableButtons();
        showSuccess('Sample dataset loaded successfully!');
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

    showLoading('Generating new graph... This may take a moment.');

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

        if (data.success) {
            currentGraphData = data.graph;
            displayMetrics(data.metrics);
            visualizeGraph(data.graph);
            showSuccess('New graph generated successfully!');
        } else {
            throw new Error(data.error || 'Generation failed');
        }
    } catch (error) {
        showError('Error generating graph: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Скачивание графа
async function downloadGraph() {
    if (!currentGraphData) return;

    const format = document.getElementById('downloadFormat').value;

    showLoading('Preparing download...');

    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                graph: currentGraphData,
                format: format
            })
        });

        if (!response.ok) {
            throw new Error('Download failed');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `generated_graph.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showSuccess('Download started!');
    } catch (error) {
        showError('Error downloading: ' + error.message);
    } finally {
        hideLoading();
    }
}

// Визуализация графа с D3.js
function visualizeGraph(graphData) {
    const container = document.getElementById('graph');
    container.innerHTML = '';

    const width = container.clientWidth;
    const height = container.clientHeight;

    const svg = d3.select('#graph')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const g = svg.append('g');

    // Создаем стрелки
    svg.append('defs').append('marker')
        .attr('id', 'arrowhead')
        .attr('viewBox', '0 -5 10 10')
        .attr('refX', 20)
        .attr('refY', 0)
        .attr('orient', 'auto')
        .attr('markerWidth', 6)
        .attr('markerHeight', 6)
        .append('path')
        .attr('d', 'M0,-5L10,0L0,5')
        .attr('fill', '#666');

    // Создаем симуляцию
    simulation = d3.forceSimulation(graphData.nodes)
        .force('link', d3.forceLink(graphData.edges).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(30));

    // Создаем линии (ребра)
    const link = g.append('g')
        .selectAll('line')
        .data(graphData.edges)
        .enter()
        .append('line')
        .attr('class', 'link')
        .attr('marker-end', 'url(#arrowhead)')
        .style('stroke', '#999')
        .style('stroke-width', 2);

    // Создаем узлы
    const node = g.append('g')
        .selectAll('circle')
        .data(graphData.nodes)
        .enter()
        .append('circle')
        .attr('class', 'node')
        .attr('r', 10)
        .attr('fill', '#667eea')
        .call(d3.drag()
            .on('start', dragStarted)
            .on('drag', dragged)
            .on('end', dragEnded));

    // Добавляем подписи
    const label = g.append('g')
        .selectAll('text')
        .data(graphData.nodes)
        .enter()
        .append('text')
        .attr('class', 'label')
        .text(d => d.id)
        .attr('font-size', '12px')
        .attr('dx', 15)
        .attr('dy', 4)
        .style('opacity', showLabels ? 1 : 0);

    // Обновление позиций
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);

        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });

    // Добавляем зум
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });

    svg.call(zoom);

    // Обработчики drag
    function dragStarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragEnded(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    // Обновляем силу при изменении слайдера
    document.getElementById('forceSlider').addEventListener('input', function() {
        const strength = this.value;
        simulation.force('charge', d3.forceManyBody().strength(-strength * 6));
        simulation.alpha(0.3).restart();
    });
}

// Отображение метрик
function displayMetrics(metrics) {
    const metricsDiv = document.getElementById('metrics');

    const metricItems = [
        { key: 'num_nodes', label: 'Nodes', format: d => d },
        { key: 'num_edges', label: 'Edges', format: d => d },
        { key: 'density', label: 'Density', format: d => parseFloat(d).toFixed(4) },
        { key: 'avg_in_degree', label: 'Avg In Degree', format: d => parseFloat(d).toFixed(2) },
        { key: 'avg_out_degree', label: 'Avg Out Degree', format: d => parseFloat(d).toFixed(2) },
        { key: 'max_in_degree', label: 'Max In Degree', format: d => d },
        { key: 'max_out_degree', label: 'Max Out Degree', format: d => d },
        { key: 'strongly_connected_nodes', label: 'Strongly Connected', format: d => d },
        { key: 'transitivity', label: 'Transitivity', format: d => parseFloat(d).toFixed(3) },
        { key: 'reciprocity', label: 'Reciprocity', format: d => parseFloat(d).toFixed(3) },
        { key: 'avg_clustering', label: 'Avg Clustering', format: d => parseFloat(d).toFixed(3) }
    ];

    let html = '<div class="metrics-grid">';
    metricItems.forEach(item => {
        if (metrics[item.key] !== undefined) {
            html += `
                <div class="metric-item">
                    <h4>${item.label}</h4>
                    <div class="metric-value">${item.format(metrics[item.key])}</div>
                </div>
            `;
        }
    });
    html += '</div>';

    metricsDiv.innerHTML = html;
}

// Отображение анализа мотивов
function displayMotifAnalysis(data) {
    const analysisDiv = document.getElementById('motifAnalysis');

    if (!data.motifs || data.motifs.length === 0) {
        analysisDiv.innerHTML = '<p>No motif data available</p>';
        return;
    }

    let html = `
        <div class="motif-summary">
            <p>Total triplets analyzed: <strong>${data.total_motifs}</strong></p>
        </div>
        <div class="motif-grid">
    `;

    data.motifs.forEach(motif => {
        const percentage = (motif.probability * 100).toFixed(2);
        html += `
            <div class="motif-item">
                <h4>M${motif.id}</h4>
                <div class="motif-count">${motif.count}</div>
                <div class="motif-probability">${percentage}%</div>
            </div>
        `;
    });

    html += '</div>';
    analysisDiv.innerHTML = html;
}

// Включение кнопок
function enableButtons() {
    document.getElementById('analyzeBtn').disabled = false;
    document.getElementById('generateBtn').disabled = false;
    document.getElementById('downloadBtn').disabled = false;
}

// Сброс вида графа
function resetView() {
    if (simulation) {
        simulation.alpha(1).restart();
    }
}

// Переключение подписей
function toggleLabels() {
    showLabels = !showLabels;
    d3.selectAll('.label').style('opacity', showLabels ? 1 : 0);
}

// Управление загрузкой
function showLoading(message) {
    document.getElementById('loadingMessage').textContent = message;
    document.getElementById('loadingModal').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingModal').classList.remove('active');
}

function showSuccess(message) {
    alert('Success: ' + message);
}

function showError(message) {
    alert('Error: ' + message);
}

// Добавляем CSS для сетки метрик
const style = document.createElement('style');
style.textContent = `
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 15px;
    }
`;
document.head.appendChild(style);