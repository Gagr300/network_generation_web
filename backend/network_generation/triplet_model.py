import networkx as nx
from dotmotif import GrandIsoExecutor
from random import randrange, choices, choice
from itertools import permutations
from typing import Callable, Optional
from .triplets import motifs, motifs_edges, motifs_digraphs


class SubgraphStructure:
    class SubgraphType:
        def __init__(self, motif, count, index) -> None:
            self.index = index
            self.motif = motif
            self.count = count
            self.nodes = set(a for a, b in motifs[0].list_edge_constraints().keys()) | set(
                b for a, b in motifs[0].list_edge_constraints().keys())
            self.probability = 0

    def __init__(self, graph, motif_types):
        self.motif_subgraphs = {}
        E = GrandIsoExecutor(graph=graph)
        self.motifs_sum = 0
        self.graph = graph
        self.inv_graph = nx.difference(nx.complete_graph(graph.nodes(), nx.DiGraph()), graph)
        E_inv = GrandIsoExecutor(graph=self.inv_graph)
        for i in range(len(motif_types)):
            if i == 0:
                motif_count = len(E_inv.find(motif_types[15]))  # full
            elif i == 1:
                motif_count = len(E_inv.find(motif_types[14]))  # oneway twoway twoway
            elif i == 2:
                motif_count = len(E_inv.find(motif_types[8]))  # noway twoway twoway
            else:
                motif_count = len(E.find(motif_types[i]))
            self.motif_subgraphs[motif_types[i]] = self.SubgraphType(motif_types[i], motif_count, i)
            self.motifs_sum += motif_count
            print(i, motif_types[i], motif_count)
        print(self.motifs_sum, self.graph)
        self.left_probabilities = [0] * len(motif_types)

        if self.motifs_sum > 0:
            for x in self.motif_subgraphs:
                self.motif_subgraphs[x].probability = self.motif_subgraphs[x].count / self.motifs_sum
                self.left_probabilities[self.motif_subgraphs[x].index] = self.motif_subgraphs[x].probability


class RandomGraphGenerator:
    def __init__(self, graph, motif_types) -> None:
        self.N = len(graph.nodes())
        self.M = len(graph.edges())
        self.subgraphStructure = SubgraphStructure(graph, motif_types)
        self.motif_types = motif_types
        self.possible_motifs = {
            0: list(range(16)),
            1: list(range(1, 16)),
            2: [2, 6, 7, 8, 11, 12, 13, 14, 15],
            3: [3, 6, 8, 10, 11, 12, 13, 14, 15],
            4: [4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            5: [5, 7, 8, 10, 11, 12, 13, 14, 15],
            6: [6, 8, 12, 13, 14, 15],
            7: [7, 8, 11, 13, 14, 15],
            8: [8, 14, 15],
            9: [9, 13, 14, 15],
            10: [10, 11, 14, 15],
            11: [11, 14, 15],
            12: [12, 14, 15],
            13: [13, 14, 15],
            14: [14, 15],
            15: [15]
        }
        self.progress_callback = None  # для отслеживания прогресса

    def set_progress_callback(self, callback: Callable[[int, int], None]):
        """Устанавливает callback для отслеживания прогресса"""
        self.progress_callback = callback

    def wegner_multiplet_model(self):
        print('wegner_multiplet_model')
        new_graph = nx.DiGraph()
        new_graph.add_nodes_from([i for i in range(self.N)])

        iteration = 0
        max_iterations = self.M * 100

        while len(new_graph.edges()) < self.M and iteration < max_iterations:

            iteration += 1

            # тройка вершин
            a, b, c = randrange(self.N), randrange(self.N), randrange(self.N)
            if a == b or b == c or a == c:
                continue

            # определение возможных мотивов
            triangle = nx.DiGraph(new_graph.subgraph([a, b, c]))
            cur_motif = [i for i in range(16) if nx.is_isomorphic(motifs_digraphs[i], triangle)][0]
            possible_motifs = [self.subgraphStructure.left_probabilities[i] for i in self.possible_motifs[cur_motif]]

            try:
                # Выбираем случайный мотив с учетом весов
                rnd_motif_subgraph = choices(self.possible_motifs[cur_motif], weights=possible_motifs)[0]
            except ValueError as e:
                # если weights все нулевые или negative, выбираем случайный
                print(f"Error: {e}")
                rnd_motif_subgraph = choice(self.possible_motifs[cur_motif])

            # Находим оптимальную перестановку вершин
            best_dict = None
            min_dif = float('inf')

            for A, B, C in permutations([a, b, c]):
                dict_nodes = {'A': A, 'B': B, 'C': C}
                triangle = nx.DiGraph(new_graph.subgraph([a, b, c]))
                # Добавляем ребра из выбранного мотива
                triangle.add_edges_from([(dict_nodes[a], dict_nodes[b])
                                         for a, b in motifs_edges[rnd_motif_subgraph]])

                # Вычисляем разницу между текущим и желаемым количеством ребер
                current_edges = len(triangle.edges())
                desired_edges = len(motifs_edges[rnd_motif_subgraph])
                dif = abs(current_edges - desired_edges)

                if dif < min_dif:
                    min_dif = dif
                    best_dict = dict_nodes

            # Добавляем ребра в граф
            if best_dict:
                new_graph.add_edges_from([(best_dict[a], best_dict[b])
                                          for a, b in motifs_edges[rnd_motif_subgraph]])

                if self.progress_callback:
                    self.progress_callback(
                        len(new_graph.edges()), self.M)

            # Обновляем структуру мотивов
            structure = SubgraphStructure(new_graph, self.motif_types)

        if iteration >= max_iterations:
            print(f"Warning: Reached maximum iterations ({max_iterations})")

        return new_graph
