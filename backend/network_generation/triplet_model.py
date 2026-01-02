import networkx as nx
from dotmotif import GrandIsoExecutor
from random import randrange, choices
from itertools import permutations
from .triplets import motifs, motifs_edges


class SubgraphStructure:
    class SubgraphType:
        def __init__(self, motif, count, index) -> None:
            self.index = index
            self.motif = motif
            self.count = count
            self.nodes = set(a for a, b in motif.list_edge_constraints().keys()) | set(
                b for a, b in motif.list_edge_constraints().keys())
            self.probability = 0

    def __init__(self, graph, motif_types):
        self.motif_subgraphs = {}
        E = GrandIsoExecutor(graph=graph)
        self.motifs_sum = 0
        self.graph = graph
        self.inv_graph = nx.difference(nx.complete_graph(graph.nodes(), nx.DiGraph()), graph)
        E_inv = GrandIsoExecutor(graph=self.inv_graph)

        for i in range(len(motif_types)):
            if i == 0:  # no edges at all
                motif_count = len(E_inv.find(motif_types[3]))  # full_graph
            elif i == 1:
                motif_count = len(E_inv.find(motif_types[2]))  # oneway twoway twoway
            elif i == 2:
                motif_count = len(E_inv.find(motif_types[12]))  # noway twoway twoway
            else:
                motif_count = len(E.find(motif_types[i]))

            self.motif_subgraphs[motif_types[i]] = self.SubgraphType(motif_types[i], motif_count, i)
            self.motifs_sum += motif_count

        self.left_probabilities = [0] * len(motif_types)

        if self.motifs_sum > 0:
            for x in self.motif_subgraphs:
                self.motif_subgraphs[x].probability = self.motif_subgraphs[x].count / self.motifs_sum
                self.left_probabilities[self.motif_subgraphs[x].index] = self.motif_subgraphs[x].probability

    def add_edges_to_graph(self, graph, motif, vertices):
        dict_nodes = {a: b for a, b in zip(self.motif_subgraphs[motif].nodes, vertices)}
        graph.add_edges_from([(dict_nodes[a], dict_nodes[b]) for a, b in motif.list_edge_constraints().keys()])
        self.left_probabilities[self.motif_subgraphs[motif].index] -= 1. / self.motifs_sum


class RandomGraphGenerator:
    def __init__(self, graph, motif_types) -> None:
        self.N = len(graph.nodes())
        self.M = len(graph.edges())
        self.subgraphStructure = SubgraphStructure(graph, motif_types)
        self.motif_types = motif_types

    def wegner_multiplet_model(self):
        self.new_graph = nx.DiGraph()
        self.new_graph.add_nodes_from([i for i in range(self.N)])
        possible_motifs = [0] * len(self.motif_types)

        while len(self.new_graph.edges()) < self.M:
            # Выбираем случайную тройку вершин
            a, b, c = randrange(self.N), randrange(self.N), randrange(self.N)
            if a == b or b == c or a == c:
                continue

            # Определяем возможные мотивы для этой тройки
            possible_motifs = [0] * len(self.motif_types)

            for i in range(4):
                for j in range(4):
                    for k in range(4):
                        triangle = nx.DiGraph(self.new_graph.subgraph([a, b, c]))

                        # Добавляем ребра между A и B
                        if i == 0:
                            triangle.add_edges_from([(a, b)])
                        elif i == 1:
                            triangle.add_edges_from([(b, a)])
                        elif i == 2:
                            triangle.add_edges_from([(a, b), (b, a)])

                        # Добавляем ребра между C и B
                        if j == 0:
                            triangle.add_edges_from([(c, b)])
                        elif j == 1:
                            triangle.add_edges_from([(b, c)])
                        elif j == 2:
                            triangle.add_edges_from([(c, b), (b, c)])

                        # Добавляем ребра между A и C
                        if k == 0:
                            triangle.add_edges_from([(a, c)])
                        elif k == 1:
                            triangle.add_edges_from([(c, a)])
                        elif k == 2:
                            triangle.add_edges_from([(a, c), (c, a)])

                        # Рассчитываем вероятности мотивов
                        structure = SubgraphStructure(triangle, self.motif_types)
                        possible_motifs = [a + b for a, b in zip(possible_motifs, structure.left_probabilities)]

            # Выбираем мотив для построения
            motif_weights = [1 if b > 0 and self.subgraphStructure.left_probabilities[a] > 0 else 0
                             for a, b in enumerate(possible_motifs)]

            if sum(motif_weights) == 0:
                continue

            rnd_motif_idx = choices([i for i in range(len(self.motif_types))], weights=motif_weights)[0]

            # Находим лучшую перестановку вершин для добавления ребер
            best_dict = None
            min_diff = float('inf')

            for A, B, C in permutations([a, b, c]):
                dict_nodes = {'A': A, 'B': B, 'C': C}
                current_edges = set(self.new_graph.edges([A, B, C]))

                # Создаем новые ребра согласно мотиву
                new_edges = {(dict_nodes[X], dict_nodes[Y]) for X, Y in motifs_edges[rnd_motif_idx]}

                # Вычисляем разницу
                diff = len(new_edges - current_edges)

                if diff < min_diff:
                    min_diff = diff
                    best_dict = dict_nodes

            # Добавляем ребра в граф
            if best_dict:
                edges_to_add = [(best_dict[X], best_dict[Y]) for X, Y in motifs_edges[rnd_motif_idx]]
                self.new_graph.add_edges_from(edges_to_add)

                # Обновляем структуру (упрощенная версия)
                self.subgraphStructure.left_probabilities[rnd_motif_idx] -= 1.0 / self.subgraphStructure.motifs_sum

        return self.new_graph