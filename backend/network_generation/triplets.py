from dotmotif import Motif
import networkx as nx

# Определение всех 16 мотивов для триплетов

motifs = [
    # M0
    Motif("""
  noWayEdge(a, b) {
      a !> b
      b !> a
  }
  noWayEdge(A, B)
  noWayEdge(B, C)
  noWayEdge(A, C)
"""),

    # M1
    Motif("""
  oneWayEdge(a, b) {
      a -> b
      b !> a
  }
  noWayEdge(a, b) {
      a !> b
      b !> a
  }
  oneWayEdge(A, B)
  noWayEdge(B, C)
  noWayEdge(A, C)
"""),

    # M2
    Motif("""
  twoWayEdge(a, b) {
      a -> b
      b -> a
  }
  noWayEdge(a, b) {
      a !> b
      b !> a
  }
  twoWayEdge(A, B)
  noWayEdge(B, C)
  noWayEdge(A, C)
"""),

    # M3
    Motif("""
  oneWayEdge(a, b) {
      a -> b
      b !> a
  }
  twoWayEdge(a, b) {
      a -> b
      b -> a
  }
  noWayEdge(a, b) {
      a !> b
      b !> a
  }
  oneWayEdge(B, A)
  oneWayEdge(B, C)
  noWayEdge(A, C)
"""),

    # M4
    Motif("""
  oneWayEdge(a, b) {
      a -> b
      b !> a
  }
  twoWayEdge(a, b) {
      a -> b
      b -> a
  }
  noWayEdge(a, b) {
      a !> b
      b !> a
  }
  oneWayEdge(B, A)
  oneWayEdge(C, B)
  noWayEdge(A, C)
"""),

    # M5
    Motif("""
  oneWayEdge(a, b) {
      a -> b
      b !> a
  }
  twoWayEdge(a, b) {
      a -> b
      b -> a
  }
  noWayEdge(a, b) {
      a !> b
      b !> a
  }
  oneWayEdge(A, B)
  oneWayEdge(C, B)
  noWayEdge(A, C)
"""),

    # M6
    Motif("""
  oneWayEdge(a, b) {
      a -> b
      b !> a
  }
  twoWayEdge(a, b) {
      a -> b
      b -> a
  }
  noWayEdge(a, b) {
      a !> b
      b !> a
  }
  twoWayEdge(A, B)
  oneWayEdge(B, C)
  noWayEdge(A, C)
"""),

    # M7
    Motif("""
  oneWayEdge(a, b) {
      a -> b
      b !> a
  }
  twoWayEdge(a, b) {
      a -> b
      b -> a
  }
  noWayEdge(a, b) {
      a !> b
      b !> a
  }
  twoWayEdge(A, B)
  oneWayEdge(C, B)
  noWayEdge(A, C)
"""),

    # M8
    Motif("""
  oneWayEdge(a, b) {
      a -> b
      b !> a
  }
  twoWayEdge(a, b) {
      a -> b
      b -> a
  }
  noWayEdge(a, b) {
      a !> b
      b !> a
  }
  twoWayEdge(A, B)
  twoWayEdge(B, C)
  noWayEdge(A, C)
"""),

    # M9
    Motif("""
  oneWayEdge(a, b) {
      a -> b
      b !> a
  }
  oneWayEdge(A, B)
  oneWayEdge(B, C)
  oneWayEdge(C, A)
"""),

    # M10
    Motif("""
  oneWayEdge(a, b) {
      a -> b
      b !> a
  }
  oneWayEdge(A, B)
  oneWayEdge(B, C)
  oneWayEdge(A, C)
"""),

    # M11
    Motif("""
  oneWayEdge(a, b) {
      a -> b
      b !> a
  }
  twoWayEdge(a, b) {
      a -> b
      b -> a
  }
  oneWayEdge(B, A)
  oneWayEdge(B, C)
  twoWayEdge(A, C)
"""),

    # M12
    Motif("""
  oneWayEdge(a, b) {
      a -> b
      b !> a
  }
  twoWayEdge(a, b) {
      a -> b
      b -> a
  }
  oneWayEdge(A, B)
  oneWayEdge(C, B)
  twoWayEdge(A, C)
"""),

    # M13
    Motif("""
  oneWayEdge(a, b) {
      a -> b
      b !> a
  }
  twoWayEdge(a, b) {
      a -> b
      b -> a
  }
  oneWayEdge(A, B)
  twoWayEdge(B, C)
  oneWayEdge(C, A)
"""),

    # M14
    Motif("""
  oneWayEdge(a, b) {
      a -> b
      b !> a
  }
  twoWayEdge(a, b) {
      a -> b
      b -> a
  }
  oneWayEdge(A, B)
  twoWayEdge(B, C)
  twoWayEdge(C, A)
"""),

    # M15
    Motif("""
  twoWayEdge(a, b) {
      a -> b
      b -> a
  }
  twoWayEdge(A, B)
  twoWayEdge(B, C)
  twoWayEdge(C, A)
""")]

# Список ребер для каждого мотива
motifs_edges = [
    [],  # M0
    [('A', 'B')],  # M1
    [('A', 'B'), ('B', 'A')],  # M2
    [('B', 'A'), ('B', 'C')],  # M3
    [('B', 'A'), ('C', 'B')],  # M4
    [('A', 'B'), ('C', 'B')],  # M5
    [('A', 'B'), ('B', 'A'), ('B', 'C')],  # M6
    [('A', 'B'), ('B', 'A'), ('C', 'B')],  # M7
    [('A', 'B'), ('B', 'A'), ('B', 'C'), ('C', 'B')],  # M8
    [('A', 'B'), ('B', 'C'), ('C', 'A')],  # M9
    [('A', 'B'), ('B', 'C'), ('A', 'C')],  # M10
    [('B', 'A'), ('B', 'C'), ('C', 'A'), ('A', 'C')],  # M11
    [('A', 'B'), ('C', 'B'), ('C', 'A'), ('A', 'C')],  # M12
    [('A', 'B'), ('B', 'C'), ('C', 'B'), ('C', 'A')],  # M13
    [('A', 'B'), ('B', 'C'), ('C', 'B'), ('C', 'A'), ('A', 'C')],  # M14
    [('A', 'B'), ('B', 'A'), ('B', 'C'), ('C', 'B'), ('C', 'A'), ('A', 'C')]  # M15
]

motifs_digraphs = [
    nx.DiGraph({'A': [], 'B': [], 'C': []}), # M0
    nx.DiGraph({'A': ['B'], 'B': [], 'C': []}), # M1
    nx.DiGraph({'A': ['B'], 'B': ['A'], 'C': []}), # M2
    nx.DiGraph({'A': [], 'B': ['A', 'C'], 'C': []}), # M3
    nx.DiGraph({'A': [], 'B': ['A'], 'C': ['B']}), # M4
    nx.DiGraph({'A': ['B'], 'B': [], 'C': ['B']}), # M5
    nx.DiGraph({'A': ['B'], 'B': ['A', 'C'], 'C': []}), # M6
    nx.DiGraph({'A': ['B'], 'B': ['A'], 'C': ['B']}), # M7
    nx.DiGraph({'A': ['B'], 'B': ['A', 'C'], 'C': ['B']}), # M8
    nx.DiGraph({'A': ['B'], 'B': ['C'], 'C': ['A']}), # M9
    nx.DiGraph({'A': ['B', 'C'], 'B': ['C'], 'C': []}), # M10
    nx.DiGraph({'A': ['C'], 'B': ['A', 'C'], 'C': ['A']}), # M11
    nx.DiGraph({'A': ['B', 'C'], 'B': [], 'C': ['B', 'A']}), # M12
    nx.DiGraph({'A': ['B'], 'B': ['C'], 'C': ['B', 'A']}), # M13
    nx.DiGraph({'A': ['B', 'C'], 'B': ['C'], 'C': ['B', 'A']}), # M14
    nx.DiGraph({'A': ['B', 'C'], 'B': ['A', 'C'], 'C': ['A', 'B']}) # M15
]
