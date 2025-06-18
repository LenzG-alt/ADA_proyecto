import unittest
import sys
import os

# Add the parent directory of 'proyecto' to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from proyecto.src.construccion_grafo import Grafo
from proyecto.src.analisis_grafo import encontrar_camino_minimo_bfs

class TestAnalisisGrafoFunctions(unittest.TestCase):

    def test_simple_path(self):
        grafo = Grafo(3)
        grafo.agregar_arista(0, 1)
        grafo.agregar_arista(1, 2)
        self.assertEqual(encontrar_camino_minimo_bfs(grafo, 0, 2), [0, 1, 2])

    def test_start_equals_end_node(self):
        grafo = Grafo(3)
        grafo.agregar_arista(0, 1)
        self.assertEqual(encontrar_camino_minimo_bfs(grafo, 0, 0), [0])

    def test_no_path_connected_graph(self):
        # Graph: 0 -> 1, 2 (node 2 is isolated by direction)
        grafo = Grafo(3)
        grafo.agregar_arista(0, 1)
        self.assertIsNone(encontrar_camino_minimo_bfs(grafo, 0, 2))
        self.assertIsNone(encontrar_camino_minimo_bfs(grafo, 2, 0))

        # More complex: 0-1, 1-2, but asking for 2-0
        grafo_2 = Grafo(3)
        grafo_2.agregar_arista(0,1)
        grafo_2.agregar_arista(1,2)
        self.assertIsNone(encontrar_camino_minimo_bfs(grafo_2, 2, 0))


    def test_nodes_in_different_disconnected_components(self):
        grafo = Grafo(4)
        # Component 1: 0 -> 1
        grafo.agregar_arista(0, 1)
        # Component 2: 2 -> 3
        grafo.agregar_arista(2, 3)
        self.assertIsNone(encontrar_camino_minimo_bfs(grafo, 0, 3))

    def test_start_node_out_of_bounds_negative(self):
        grafo = Grafo(3)
        # Function is expected to print an error and return None
        self.assertIsNone(encontrar_camino_minimo_bfs(grafo, -1, 2))

    def test_start_node_out_of_bounds_too_large(self):
        grafo = Grafo(3)
        self.assertIsNone(encontrar_camino_minimo_bfs(grafo, 3, 1))

    def test_end_node_out_of_bounds_negative(self):
        grafo = Grafo(3)
        self.assertIsNone(encontrar_camino_minimo_bfs(grafo, 0, -2))

    def test_end_node_out_of_bounds_too_large(self):
        grafo = Grafo(3)
        self.assertIsNone(encontrar_camino_minimo_bfs(grafo, 0, 3))

    def test_both_nodes_out_of_bounds(self):
        grafo = Grafo(3)
        self.assertIsNone(encontrar_camino_minimo_bfs(grafo, -1, 3))

    def test_path_length_greater_than_one(self):
        # 0 -> 1 -> 2 -> 3
        grafo = Grafo(4)
        grafo.agregar_arista(0, 1)
        grafo.agregar_arista(1, 2)
        grafo.agregar_arista(2, 3)
        self.assertEqual(encontrar_camino_minimo_bfs(grafo, 0, 3), [0, 1, 2, 3])

    def test_path_with_multiple_options_chooses_shortest(self):
        grafo = Grafo(4)
        grafo.agregar_arista(0, 1)
        grafo.agregar_arista(1, 3) # Path 0-1-3 (length 2)
        grafo.agregar_arista(0, 2)
        grafo.agregar_arista(2, 3) # Path 0-2-3 (length 2)

        # BFS should find one of them. The exact one can depend on iteration order over neighbors.
        # Let's add a longer path too:
        grafo.agregar_arista(0,0) # self loop
        grafo.agregar_arista(1,2) # 0-1-2-3 (length 3)

        path = encontrar_camino_minimo_bfs(grafo, 0, 3)
        self.assertIsNotNone(path)
        self.assertEqual(len(path) - 1, 2) # Length of path should be 2
        # Possible paths: [0,1,3] or [0,2,3]. We check if it's one of them.
        self.assertIn(path, [[0,1,3], [0,2,3]])


    def test_empty_graph_zero_nodes(self):
        grafo = Grafo(0)
        # encontrar_camino_minimo_bfs checks for num_nodos == 0
        self.assertIsNone(encontrar_camino_minimo_bfs(grafo, 0, 0))

    def test_graph_with_one_node_path_to_self(self):
        grafo = Grafo(1)
        self.assertEqual(encontrar_camino_minimo_bfs(grafo, 0, 0), [0])

    def test_graph_with_one_node_path_to_other_fails(self):
        grafo = Grafo(1)
        self.assertIsNone(encontrar_camino_minimo_bfs(grafo, 0, 1)) # Target out of bounds

    def test_no_path_due_to_edge_direction(self):
        grafo = Grafo(3)
        grafo.agregar_arista(0,1)
        grafo.agregar_arista(2,1) # 0 -> 1 <- 2
        self.assertIsNone(encontrar_camino_minimo_bfs(grafo,0,2)) # No path from 0 to 2
        self.assertEqual(encontrar_camino_minimo_bfs(grafo,0,1), [0,1])

    def test_path_in_larger_graph_with_cycles(self):
        grafo = Grafo(5)
        grafo.agregar_arista(0, 1)
        grafo.agregar_arista(1, 2)
        grafo.agregar_arista(2, 0) # Cycle 0-1-2-0
        grafo.agregar_arista(1, 3)
        grafo.agregar_arista(3, 4) # Path 0-1-3-4

        self.assertEqual(encontrar_camino_minimo_bfs(grafo, 0, 4), [0, 1, 3, 4])
        self.assertEqual(encontrar_camino_minimo_bfs(grafo, 0, 2), [0, 1, 2]) # Shortest to 2

if __name__ == '__main__':
    unittest.main()
