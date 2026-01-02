from dotmotif import Motif

# Определение всех 16 мотивов для триплетов

motifs = []

# M0 (0) - No edges
motifs.append(Motif("""
  noWayEdge(a, b) {
      a !> b
      b !> a
  }
  noWayEdge(A, B)
  noWayEdge(B, C)
  noWayEdge(A, C)
"""))

# M1 (1) - One directed edge
motifs.append(Motif("""
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
"""))

# M2 (2) - Bidirectional edge
motifs.append(Motif("""
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
"""))

# M3 (3)
motifs.append(Motif("""
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
"""))

# M4 (4)
motifs.append(Motif("""
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
"""))

# M5 (5)
motifs.append(Motif("""
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
"""))

# M6 (6)
motifs.append(Motif("""
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
"""))

# M7 (7)
motifs.append(Motif("""
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
"""))

# M8 (8)
motifs.append(Motif("""
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
"""))

# M9 (9) - Directed triangle (one direction)
motifs.append(Motif("""
  oneWayEdge(a, b) {
      a -> b
      b !> a
  }
  oneWayEdge(A, B)
  oneWayEdge(B, C)
  oneWayEdge(C, A)
"""))

# M10 (10) - Two directed edges, one missing
motifs.append(Motif("""
  oneWayEdge(a, b) {
      a -> b
      b !> a
  }
  oneWayEdge(A, B)
  oneWayEdge(B, C)
  oneWayEdge(A, C)
"""))

# M11 (11)
motifs.append(Motif("""
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
"""))

# M12 (12)
motifs.append(Motif("""
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
"""))

# M13 (13)
motifs.append(Motif("""
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
"""))

# M14 (14)
motifs.append(Motif("""
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
"""))

# M15 (15) - Complete bidirectional triangle
motifs.append(Motif("""
  twoWayEdge(a, b) {
      a -> b
      b -> a
  }
  twoWayEdge(A, B)
  twoWayEdge(B, C)
  twoWayEdge(C, A)
"""))

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