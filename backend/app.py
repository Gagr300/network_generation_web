import os
import json
import networkx as nx
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import tempfile
from network_generation.triplet_model import RandomGraphGenerator, motifs
from network_generation.utils import graph_to_json, calculate_graph_metrics

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Создаем папку для временных файлов
UPLOAD_FOLDER = tempfile.mkdtemp()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def serve_index():
    """Обслуживание главной страницы"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Обслуживание статических файлов"""
    return send_from_directory(app.static_folder, path)


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

        return jsonify({
            'success': True,
            'metrics': metrics,
            'graph': graph_json
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Удаляем временный файл
        if os.path.exists(filepath):
            os.remove(filepath)


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
                'probability': motif.probability
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
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'.{format_type}')
        filepath = temp_file.name
        temp_file.close()

        if format_type == 'txt':
            with open(filepath, 'w') as f:
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

        return send_file(
            filepath,
            as_attachment=True,
            download_name=f'generated_graph.{format_type}',
            mimetype='text/plain'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Удаляем временный файл после отправки
        if os.path.exists(filepath):
            import time
            time.sleep(1)  # Даем время на отправку файла
            try:
                os.remove(filepath)
            except:
                pass


@app.route('/api/sample', methods=['GET'])
def get_sample_data():
    """Получение примера данных"""
    try:
        # Создаем более интересный пример графа
        G = nx.DiGraph()

        # Добавляем узлы с тематическими именами
        countries = [
            "USA", "China", "Germany", "Japan", "UK",
            "France", "Canada", "Australia", "India", "Brazil",
            "Russia", "Italy", "Spain", "Mexico", "South_Korea"
        ]

        for country in countries:
            G.add_node(country)

        # Добавляем реалистичные торговые связи
        trade_routes = [
            ("USA", "China"), ("China", "USA"),
            ("USA", "Canada"), ("Canada", "USA"),
            ("Germany", "France"), ("France", "Germany"),
            ("Germany", "Italy"), ("Italy", "Germany"),
            ("Japan", "USA"), ("USA", "Japan"),
            ("Japan", "China"), ("China", "Japan"),
            ("UK", "USA"), ("USA", "UK"),
            ("UK", "Germany"), ("Germany", "UK"),
            ("Brazil", "USA"), ("USA", "Brazil"),
            ("Russia", "China"), ("China", "Russia"),
            ("India", "USA"), ("USA", "India"),
            ("Australia", "China"), ("China", "Australia"),
            ("Mexico", "USA"), ("USA", "Mexico"),
            ("South_Korea", "Japan"), ("Japan", "South_Korea"),
            ("South_Korea", "USA"), ("USA", "South_Korea"),
            ("Spain", "France"), ("France", "Spain"),
            ("Spain", "Germany"), ("Germany", "Spain"),
            ("Italy", "France"), ("France", "Italy"),
            ("Canada", "China"), ("China", "Canada"),
            ("Brazil", "China"), ("China", "Brazil")
        ]

        for source, target in trade_routes:
            G.add_edge(source, target)

        # Рассчитываем метрики
        metrics = calculate_graph_metrics(G)

        # Конвертируем граф в JSON
        graph_json = graph_to_json(G)

        return jsonify({
            'success': True,
            'metrics': metrics,
            'graph': graph_json
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Проверяем наличие папок
    if not os.path.exists(app.static_folder):
        print(f"Warning: Static folder {app.static_folder} not found!")
        print("Make sure frontend files are in the correct location.")

    app.run(debug=True, port=5000)
