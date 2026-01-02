import networkx as nx
import numpy as np


def graph_to_json(G):
    """Конвертирует граф NetworkX в JSON формат"""
    nodes = [{"id": str(node)} for node in G.nodes()]
    edges = [{"source": str(source), "target": str(target)} for source, target in G.edges()]

    return {
        "nodes": nodes,
        "edges": edges
    }


def calculate_graph_metrics(G):
    """Рассчитывает основные метрики графа"""
    metrics = {}

    # Основные метрики
    metrics['num_nodes'] = G.number_of_nodes()
    metrics['num_edges'] = G.number_of_edges()
    metrics['density'] = nx.density(G)

    # Степени
    if metrics['num_nodes'] > 0:
        in_degrees = [d for n, d in G.in_degree()]
        out_degrees = [d for n, d in G.out_degree()]

        metrics['avg_in_degree'] = sum(in_degrees) / metrics['num_nodes']
        metrics['avg_out_degree'] = sum(out_degrees) / metrics['num_nodes']
        metrics['max_in_degree'] = max(in_degrees) if in_degrees else 0
        metrics['max_out_degree'] = max(out_degrees) if out_degrees else 0

    # Сильная связность
    strong_components = list(nx.strongly_connected_components(G))
    if strong_components:
        largest_strong = max(strong_components, key=len)
        metrics['strongly_connected_nodes'] = len(largest_strong)
        G_strong = G.subgraph(largest_strong)
        if len(largest_strong) > 1:
            metrics['transitivity'] = nx.transitivity(G_strong)
        else:
            metrics['transitivity'] = 0
    else:
        metrics['strongly_connected_nodes'] = 0
        metrics['transitivity'] = 0

    # Реципрокность
    try:
        metrics['reciprocity'] = nx.overall_reciprocity(G)
    except:
        metrics['reciprocity'] = 0

    # Коэффициент кластеризации
    try:
        clustering = nx.clustering(G)
        metrics['avg_clustering'] = sum(clustering.values()) / len(clustering)
    except:
        metrics['avg_clustering'] = 0

    return metrics