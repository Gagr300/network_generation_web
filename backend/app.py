import os
import json
import networkx as nx
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tempfile
from network_generation.triplet_model import RandomGraphGenerator, motifs
from network_generation.utils import graph_to_json, calculate_graph_metrics

app = Flask(__name__)
CORS(app)

# Создаем папку для временных файлов
UPLOAD_FOLDER = tempfile.mkdtemp()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/api/upload', methods=['POST'])
def upload_graph():
    """Загрузка графа из файла"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Сохраняем файл временно
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    try:
        # Пытаемся прочитать граф
        if file.filename.endswith('.txt'):
            # Предполагаем формат edge list
            G = nx.read_edgelist(filepath, create_using=nx.DiGraph())
        elif file.filename.endswith('.gml'):
            G = nx.read_gml(filepath)
        elif file.filename.endswith('.gexf'):
            G = nx.read_gexf(filepath)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400

        # Рассчитываем метрики
        metrics = calculate_graph_metrics(G)

        # Конвертируем граф в JSON для фронтенда
        graph_json = graph_to_json(G)

        # Сохраняем граф в сессии (в реальном приложении использовали бы базу данных или сессии)
        request.environ['graph'] = G

        return jsonify({
            'success': True,
            'metrics': metrics,
            'graph': graph_json
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate', methods=['POST'])
def generate_graph():
    """Генерация нового графа"""
    data = request.json
    original_graph = data.get('original_graph')

    if not original_graph:
        return jsonify({'error': 'No graph data provided'}), 400

    try:
        # Восстанавливаем граф из JSON
        G = nx.DiGraph()
        for node in original_graph['nodes']:
            G.add_node(node['id'])
        for edge in original_graph['edges']:
            G.add_edge(edge['source'], edge['target'])

        # Генерируем новый граф
        generator = RandomGraphGenerator(G, motifs)
        new_G = generator.wegner_multiplet_model()

        # Рассчитываем метрики
        metrics = calculate_graph_metrics(new_G)

        # Конвертируем в JSON
        graph_json = graph_to_json(new_G)

        return jsonify({
            'success': True,
            'metrics': metrics,
            'graph': graph_json
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_graph():
    """Анализ мотивов в графе"""
    data = request.json
    graph_data = data.get('graph')

    if not graph_data:
        return jsonify({'error': 'No graph data provided'}), 400

    try:
        # Восстанавливаем граф из JSON
        G = nx.DiGraph()
        for node in graph_data['nodes']:
            G.add_node(node['id'])
        for edge in graph_data['edges']:
            G.add_edge(edge['source'], edge['target'])

        # Анализ мотивов
        generator = RandomGraphGenerator(G, motifs)
        structure = generator.subgraphStructure

        # Собираем информацию о мотивах
        motifs_info = []
        for motif in structure.motif_subgraphs.values():
            motifs_info.append({
                'id': motif.index,
                'count': motif.count,
                'probability': motif.probability,
                'edges': list(motif.motif.list_edge_constraints().keys())
            })

        return jsonify({
            'success': True,
            'motifs': motifs_info,
            'total_motifs': structure.motifs_sum
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download', methods=['POST'])
def download_graph():
    """Скачивание графа в различных форматах"""
    data = request.json
    graph_data = data.get('graph')
    format_type = data.get('format', 'txt')

    if not graph_data:
        return jsonify({'error': 'No graph data provided'}), 400

    try:
        # Восстанавливаем граф
        G = nx.DiGraph()
        for node in graph_data['nodes']:
            G.add_node(node['id'])
        for edge in graph_data['edges']:
            G.add_edge(edge['source'], edge['target'])

        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{format_type}') as f:
            filepath = f.name

            if format_type == 'txt':
                for edge in G.edges():
                    f.write(f"{edge[0]} {edge[1]}\n")
            elif format_type == 'gml':
                nx.write_gml(G, filepath)
            elif format_type == 'gexf':
                nx.write_gexf(G, filepath)
            elif format_type == 'graphml':
                nx.write_graphml(G, filepath)
            else:
                return jsonify({'error': 'Unsupported format'}), 400

        return send_file(filepath, as_attachment=True, download_name=f'generated_graph.{format_type}')

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)