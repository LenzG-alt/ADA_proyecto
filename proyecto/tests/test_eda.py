import unittest
import sys
import os

# Adjust path to import from parent directory's src
# This is a common way to handle imports in tests when the test runner is executed from the project root
# or when tests are in a subdirectory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.eda import calcular_in_grados, top_n_usuarios_por_seguidores

class TestEdaFunctions(unittest.TestCase):

    def test_calcular_in_grados_empty_graph(self):
        conexiones = []
        expected_in_grados = []
        self.assertEqual(calcular_in_grados(conexiones), expected_in_grados)

    def test_calcular_in_grados_simple_graph(self):
        # 0 -> 1
        # 1 -> 2
        # 2 -> 0
        # 0 -> 2 (additional edge to test multiple incoming)
        conexiones = [
            [1, 2],  # User 0 follows 1 and 2
            [2],     # User 1 follows 2
            [0]      # User 2 follows 0
        ]
        # In-degrees:
        # Node 0: 1 (from 2)
        # Node 1: 1 (from 0)
        # Node 2: 2 (from 0, from 1)
        expected_in_grados = [1, 1, 2]
        self.assertEqual(calcular_in_grados(conexiones), expected_in_grados)

    def test_calcular_in_grados_no_incoming_edges(self):
        # 0 -> 1
        # 2 (no outgoing, no incoming from 0 or 1)
        conexiones = [
            [1], # User 0 follows 1
            [],  # User 1 follows no one
            []   # User 2 follows no one
        ]
        # In-degrees:
        # Node 0: 0
        # Node 1: 1 (from 0)
        # Node 2: 0
        expected_in_grados = [0, 1, 0]
        self.assertEqual(calcular_in_grados(conexiones), expected_in_grados)

    def test_calcular_in_grados_all_point_to_one_node(self):
        # 0 -> 2
        # 1 -> 2
        # 2 (follows no one)
        conexiones = [
            [2], # User 0 follows 2
            [2], # User 1 follows 2
            []   # User 2 follows no one
        ]
        # In-degrees:
        # Node 0: 0
        # Node 1: 0
        # Node 2: 2 (from 0, from 1)
        expected_in_grados = [0, 0, 2]
        self.assertEqual(calcular_in_grados(conexiones), expected_in_grados)

    def test_calcular_in_grados_out_of_bounds_edge(self):
        # User 0 follows user 5 (who doesn't exist in a 3-user graph)
        conexiones = [
            [5],
            [],
            []
        ]
        # In-degrees should still be calculated for existing users
        # Node 0: 0
        # Node 1: 0
        # Node 2: 0
        # The function should handle this gracefully by not incrementing non-existent user's in-degree
        expected_in_grados = [0, 0, 0]
        self.assertEqual(calcular_in_grados(conexiones), expected_in_grados)

    # Tests for top_n_usuarios_por_seguidores

    def test_top_n_empty_in_grados(self):
        conexiones = [] # or based on num_usuarios from in_grados
        in_grados = []
        n = 5
        # If conexiones is used to determine num_usuarios, it should be []
        # If in_grados implies num_usuarios, then num_usuarios is 0
        self.assertEqual(top_n_usuarios_por_seguidores([], in_grados, n), [])

    def test_top_n_zero_n(self):
        conexiones = [[1], [0], []] # 3 users
        in_grados = [1, 1, 0]
        n = 0
        self.assertEqual(top_n_usuarios_por_seguidores(conexiones, in_grados, n), [])

    def test_top_n_less_than_total(self):
        # User IDs: 0, 1, 2, 3
        # In-degrees: User 0: 2, User 1: 3, User 2: 1, User 3: 0
        conexiones = [[], [], [], []] # Dummy conexiones, length matters
        in_grados = [2, 3, 1, 0]
        n = 2
        # Expected: [(User 1, 3 followers), (User 0, 2 followers)]
        expected_top = [(1, 3), (0, 2)]
        self.assertEqual(top_n_usuarios_por_seguidores(conexiones, in_grados, n), expected_top)

    def test_top_n_equal_to_total(self):
        conexiones = [[], [], []] # 3 users
        in_grados = [2, 3, 1]
        n = 3
        # Expected: [(User 1, 3), (User 0, 2), (User 2, 1)]
        expected_top = [(1, 3), (0, 2), (2, 1)]
        self.assertEqual(top_n_usuarios_por_seguidores(conexiones, in_grados, n), expected_top)

    def test_top_n_greater_than_total(self):
        conexiones = [[], [], []] # 3 users
        in_grados = [2, 3, 1]
        n = 5 # Asking for more users than available
        # Expected: All users, sorted: [(User 1, 3), (User 0, 2), (User 2, 1)]
        expected_top = [(1, 3), (0, 2), (2, 1)]
        self.assertEqual(top_n_usuarios_por_seguidores(conexiones, in_grados, n), expected_top)

    def test_top_n_with_ties(self):
        conexiones = [[], [], [], []] # 4 users
        # In-degrees: User 0: 2, User 1: 3, User 2: 3, User 3: 1
        in_grados = [2, 3, 3, 1]
        n = 3
        # Expected: [(User 1, 3), (User 2, 3), (User 0, 2)] or [(User 2,3), (User 1,3), (User 0,2)]
        # Python's sort is stable, so original order of tied elements is preserved.
        # If (1,3) came before (2,3) in the initial list of tuples, it will remain so.
        # Let's check based on how list comprehension + sort works:
        # users_with_seguidores = [(0,2), (1,3), (2,3), (3,1)]
        # sorted: [(1,3), (2,3), (0,2), (3,1)]
        # top 3: [(1,3), (2,3), (0,2)]
        expected_top = [(1, 3), (2, 3), (0, 2)]
        actual_top = top_n_usuarios_por_seguidores(conexiones, in_grados, n)
        self.assertEqual(actual_top, expected_top)

    def test_top_n_with_ties_different_n(self):
        conexiones = [[], [], [], []]
        in_grados = [2, 3, 3, 1] # Ties: (1,3), (2,3)
        n = 2
        # Expected: [(1,3), (2,3)]
        expected_top = [(1, 3), (2, 3)]
        actual_top = top_n_usuarios_por_seguidores(conexiones, in_grados, n)
        self.assertEqual(actual_top, expected_top)

    def test_top_n_complex_case(self):
        # conexiones are only used for len() in the current top_n_... function,
        # so we can simplify them if in_grados are provided directly.
        conexiones = [[] for _ in range(5)] # 5 users
        in_grados = [10, 5, 20, 5, 15] # User2 (20), User4 (15), User0 (10), User1 (5), User3 (5)
        n = 3
        expected = [(2, 20), (4, 15), (0, 10)]
        self.assertEqual(top_n_usuarios_por_seguidores(conexiones, in_grados, n), expected)

        n = 5
        expected_full = [(2, 20), (4, 15), (0, 10), (1, 5), (3, 5)] # Tie between 1 and 3, original order preserved
        self.assertEqual(top_n_usuarios_por_seguidores(conexiones, in_grados, n), expected_full)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

# To run these tests from the root of 'proyecto' typically:
# python -m unittest tests.test_eda
# or allow discovery:
# python -m unittest discover tests
#
# The sys.path modification is a common workaround for direct script execution
# or when the test runner's CWD isn't the project root in a way that Python resolves modules naturally.
# For more robust solutions, packaging the project (e.g. with setup.py) is recommended
# or ensuring the PYTHONPATH is set correctly in the test environment.
# Given the constraints of this environment, this sys.path adjustment is a practical approach.
# The 'proyecto' directory itself should be in PYTHONPATH for 'from src.eda import ...' to work
# if 'src' is a direct child of 'proyecto'.
# If 'proyecto.src.eda' is the module path, then 'sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))'
# might be needed if running from 'proyecto/tests/' and 'proyecto' is the top-level package.
#
# The current `sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))`
# adds the `proyecto` directory to sys.path. So, imports should be `from src.eda import ...`
# if `src` is a folder under `proyecto`.
#
# If the functions are in `proyecto/src/eda.py`, and `proyecto` is the root for module resolution,
# then `from proyecto.src.eda import ...` is how you'd import in `main.py`.
# For tests in `proyecto/tests/test_eda.py` to use the same import style,
# the `PYTHONPATH` would need to include the directory *containing* `proyecto`.
#
# Let's assume the execution environment or test runner handles `PYTHONPATH` such that
# `proyecto` is treated as a package or `proyecto.src` is.
# The provided solution in `main.py` uses `import proyecto.src.eda as eda`.
# This means `proyecto` is a top-level package.
# So, from `proyecto/tests/test_eda.py`, to import `proyecto.src.eda`,
# the directory *containing* `proyecto` must be in `sys.path`.
# The current `sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))`
# adds `proyecto` to `sys.path`. This means imports should be `from src.eda ...`
#
# Let's adjust the import to be consistent with `main.py`'s style, assuming the test runner
# will execute from a context where `proyecto` is a recognizable package.
# If `main.py` is `proyecto/src/main.py` and uses `import proyecto.src.eda`, that's a bit circular.
# Let's re-check `main.py` structure.
# `main.py` uses `import proyecto.src.eda as eda` and `from proyecto.src.analisis_grafo ...`.
# This implies that the Python interpreter is likely run from the directory *containing* `proyecto`.
#
# For the tests, if we are in `proyecto/tests/`, and `main.py` is in `proyecto/src/`:
# `sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))`
# would add the parent of `proyecto` to the path. Then `from proyecto.src.eda import ...` should work.
# I will use this path adjustment.

# Final path adjustment attempt based on typical project structures if `proyecto` is the root package.
# This adds the directory *containing* 'proyecto' to sys.path.
# So if the structure is /some_workspace/proyecto/tests/test_eda.py,
# it adds /some_workspace/ to sys.path.
# Then, `from proyecto.src.eda import ...` should work.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from proyecto.src.eda import calcular_in_grados, top_n_usuarios_por_seguidores
# Remove the previous sys.path modification and import to avoid confusion. This block will be re-inserted by the tool.
# The tool will only take the content after the filename.
# The above lines with sys.path and import are notes for myself and will be part of the generated file content.
# The actual `sys.path.insert` and `from proyecto.src.eda import ...` should be at the top of the file.
# The tool will generate the file with the content below.
# I'll remove the duplicate sys.path and import from the actual content to be written.
# The `sys.path.insert` and the corrected import `from proyecto.src.eda import ...` will be placed
# at the beginning of the file content when the tool call is made.
# The comments about path are for reasoning and won't be duplicated.
# The final version of the file will have one sys.path adjustment and one set of imports.
# This is a bit complex due to the nature of text generation.
# The actual file block starts below "proyecto/tests/test_eda.py"
#
# I will structure the file content with the correct path adjustment first, then the imports, then the class.
# The previous lines were my thought process. The actual file content for the tool starts below.
#
# Corrected structure for the file content:
# 1. sys.path modification to allow `from proyecto.src.eda import ...`
# 2. import unittest
# 3. from proyecto.src.eda import ...
# 4. Test class and methods
#
# The tool takes the filename on one line, then the content.
# So the sys.path logic needs to be *inside* the content block.
#
# Let's simplify: Assume the test runner or environment sets up PYTHONPATH correctly.
# If not, the `sys.path.insert` is a common workaround.
# The `main.py` uses `import proyecto.src.eda as eda`.
# This means the directory *containing* `proyecto` must be on PYTHONPATH.
# So, in `proyecto/tests/test_eda.py`, the same import `from proyecto.src.eda import ...` should work
# if the test runner (e.g. `python -m unittest`) is invoked from that same directory,
# or if PYTHONPATH is set appropriately.
# For now, I will include the `sys.path` modification that adds the parent of `proyecto`
# to the path, making `from proyecto.src.eda import ...` robust.
#
# The file will look like:
# import unittest
# import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# from proyecto.src.eda import calcular_in_grados, top_n_usuarios_por_seguidores
#
# class TestEdaFunctions(unittest.TestCase):
#   ... tests ...
#
# if __name__ == '__main__':
#   unittest.main() # Simplified for typical test discovery
#
# The `unittest.main(argv=['first-arg-is-ignored'], exit=False)` is often for specific environments
# like Jupyter notebooks. For a .py file, `unittest.main()` is standard.
#
# I will provide the full content for `test_eda.py` below.
# The directory `proyecto/tests` will be created by the tool if it doesn't exist.
#
# Final check on imports:
# - `main.py` is in `proyecto/src/main.py`.
# - `eda.py` is in `proyecto/src/eda.py`.
# - `main.py` uses `import proyecto.src.eda as eda`. This means that the path added to `sys.path` allows `proyecto` to be recognized as a package. This usually means the directory *containing* `proyecto` is in `sys.path`.
# - Test file is `proyecto/tests/test_eda.py`.
# - To use `from proyecto.src.eda import ...`, the directory containing `proyecto` must be in `sys.path`.
# - `os.path.dirname(__file__)` is `proyecto/tests`.
# - `os.path.join(os.path.dirname(__file__), '..')` is `proyecto`.
# - `os.path.join(os.path.dirname(__file__), '..', '..')` is the parent of `proyecto`. This is correct.

import unittest
import sys
import os

# Add the parent directory of 'proyecto' to sys.path
# This allows imports like 'from proyecto.src.module import ...'
# Structure: /<some_parent_dir>/proyecto/src/eda.py
#            /<some_parent_dir>/proyecto/tests/test_eda.py
# __file__ is <...>/proyecto/tests/test_eda.py
# os.path.dirname(__file__) is <...>/proyecto/tests
# os.path.join(os.path.dirname(__file__), '..', '..') is <...>/ (the parent of proyecto)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from proyecto.src.eda import calcular_in_grados, top_n_usuarios_por_seguidores

class TestEdaFunctions(unittest.TestCase):

    # --- Tests for calcular_in_grados ---

    def test_calcular_in_grados_empty_graph(self):
        conexiones = []
        expected_in_grados = []
        self.assertEqual(calcular_in_grados(conexiones), expected_in_grados)

    def test_calcular_in_grados_simple_graph(self):
        conexiones = [
            [1, 2],  # User 0 follows 1 and 2
            [2],     # User 1 follows 2
            [0]      # User 2 follows 0
        ]
        # Expected in-degrees: Node 0:1 (from 2), Node 1:1 (from 0), Node 2:2 (from 0,1)
        expected_in_grados = [1, 1, 2]
        self.assertEqual(calcular_in_grados(conexiones), expected_in_grados)

    def test_calcular_in_grados_node_with_no_incoming_edges(self):
        conexiones = [
            [1], # User 0 follows 1
            [],  # User 1 follows no one
            [1]  # User 2 follows 1
        ]
        # Expected in-degrees: Node 0:0, Node 1:2 (from 0,2), Node 2:0
        expected_in_grados = [0, 2, 0]
        self.assertEqual(calcular_in_grados(conexiones), expected_in_grados)

    def test_calcular_in_grados_node_all_others_point_to(self):
        conexiones = [
            [2], # User 0 follows 2
            [2], # User 1 follows 2
            []   # User 2 follows no one (but 0 and 1 follow User 2)
        ]
        # Expected in-degrees: Node 0:0, Node 1:0, Node 2:2 (from 0,1)
        expected_in_grados = [0, 0, 2]
        self.assertEqual(calcular_in_grados(conexiones), expected_in_grados)

    def test_calcular_in_grados_self_loop(self):
        conexiones = [
            [0], # User 0 follows 0
            [0]  # User 1 follows 0
        ]
        # Expected in-degrees: Node 0:2 (from 0,1), Node 1:0
        expected_in_grados = [2, 0]
        self.assertEqual(calcular_in_grados(conexiones), expected_in_grados)

    def test_calcular_in_grados_disconnected_nodes(self):
        conexiones = [
            [], # User 0
            [], # User 1
            []  # User 2
        ]
        expected_in_grados = [0, 0, 0]
        self.assertEqual(calcular_in_grados(conexiones), expected_in_grados)

    def test_calcular_in_grados_handles_out_of_bounds_target_gracefully(self):
        # User 0 follows User 5 (who is out of bounds for a 3-user graph)
        conexiones = [
            [1, 5], # User 0 follows 1 and (non-existent) 5
            [],     # User 1 follows no one
            [0]      # User 2 follows 0
        ]
        # Expected: Node 0:1 (from 2), Node 1:1 (from 0), Node 2:0. Edge to 5 is ignored.
        expected_in_grados = [1, 1, 0]
        self.assertEqual(calcular_in_grados(conexiones), expected_in_grados)


    # --- Tests for top_n_usuarios_por_seguidores ---

    def test_top_n_empty_list(self):
        # conexiones is used for len(), so if in_grados is empty, conexiones should also represent 0 users
        self.assertEqual(top_n_usuarios_por_seguidores(conexiones=[], in_grados=[], n=5), [])

    def test_top_n_ask_for_zero_users(self):
        in_grados = [1, 2, 0]
        # The `conexiones` parameter for `top_n_usuarios_por_seguidores` is used to determine
        # the number of users if needed, but `in_grados` length is primary.
        # Let's make `conexiones` consistent with `in_grados` length.
        conexiones_dummy = [[] for _ in range(len(in_grados))]
        self.assertEqual(top_n_usuarios_por_seguidores(conexiones_dummy, in_grados, 0), [])

    def test_top_n_less_than_total_users(self):
        in_grados = [2, 3, 1, 0] # User1 (3), User0 (2), User2 (1), User3 (0)
        conexiones_dummy = [[] for _ in range(len(in_grados))]
        expected = [(1, 3), (0, 2)]
        self.assertEqual(top_n_usuarios_por_seguidores(conexiones_dummy, in_grados, 2), expected)

    def test_top_n_equal_to_total_users(self):
        in_grados = [2, 3, 1] # User1 (3), User0 (2), User2 (1)
        conexiones_dummy = [[] for _ in range(len(in_grados))]
        expected = [(1, 3), (0, 2), (2, 1)]
        self.assertEqual(top_n_usuarios_por_seguidores(conexiones_dummy, in_grados, 3), expected)

    def test_top_n_greater_than_total_users(self):
        in_grados = [2, 3, 1] # User1 (3), User0 (2), User2 (1)
        conexiones_dummy = [[] for _ in range(len(in_grados))]
        expected = [(1, 3), (0, 2), (2, 1)] # Should return all, sorted
        self.assertEqual(top_n_usuarios_por_seguidores(conexiones_dummy, in_grados, 5), expected)

    def test_top_n_with_ties_in_follower_count(self):
        # User0:2, User1:3, User2:3, User3:1. Tie between User1 and User2.
        in_grados = [2, 3, 3, 1]
        conexiones_dummy = [[] for _ in range(len(in_grados))]
        # Python's sort is stable. If (1,3) appears before (2,3) in the intermediate list
        # (which it does if created by iterating user IDs 0,1,2,3), it stays that way.
        # Intermediate: [(0,2), (1,3), (2,3), (3,1)] -> Sorted: [(1,3), (2,3), (0,2), (3,1)]
        expected_top_3 = [(1, 3), (2, 3), (0, 2)]
        self.assertEqual(top_n_usuarios_por_seguidores(conexiones_dummy, in_grados, 3), expected_top_3)

        expected_top_2 = [(1, 3), (2, 3)]
        self.assertEqual(top_n_usuarios_por_seguidores(conexiones_dummy, in_grados, 2), expected_top_2)

    def test_top_n_all_users_have_same_follower_count(self):
        in_grados = [5, 5, 5]
        conexiones_dummy = [[] for _ in range(len(in_grados))]
        # Expected: order by user ID due to stable sort of (user_id, count) tuples
        expected = [(0, 5), (1, 5), (2, 5)]
        self.assertEqual(top_n_usuarios_por_seguidores(conexiones_dummy, in_grados, 3), expected)
        self.assertEqual(top_n_usuarios_por_seguidores(conexiones_dummy, in_grados, 2), expected[:2])

if __name__ == '__main__':
    # This allows running the tests directly from this file: python proyecto/tests/test_eda.py
    # Note: If run this way, the sys.path manipulation at the top is crucial.
    unittest.main()
