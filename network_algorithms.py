# network_algorithms.py
import collections
import math
import random
import heapq # Para Prim
from tqdm import tqdm

# --- 1. Análisis de Camino Más Corto (BFS) ---

def bfs_shortest_paths(graph, start_node):
    if start_node not in graph.get_nodes():
        return {}
    queue = collections.deque([(start_node, 0)])
    distances = {start_node: 0}
    while queue:
        current_node, dist = queue.popleft()
        for neighbor in graph.adj.get(current_node, []):
            if neighbor not in distances:
                distances[neighbor] = dist + 1
                queue.append((neighbor, dist + 1))
    return distances

def average_shortest_path_length(graph, sample_size=None):
    all_nodes = graph.get_nodes()
    if not all_nodes: return 0.0
    nodes_to_process = []
    if sample_size is None or sample_size >= len(all_nodes):
        nodes_to_process = all_nodes
    else:
        actual_sample_size = min(max(0, sample_size), len(all_nodes))
        if actual_sample_size == 0: return 0.0
        nodes_to_process = random.sample(all_nodes, actual_sample_size)
    if not nodes_to_process: return 0.0
    total_path_length, num_paths_found = 0, 0

    # Progress bar for iterating through source nodes for BFS
    # print(f"Calculating average shortest path length (processing {len(nodes_to_process)} source nodes)...")
    for start_node in tqdm(nodes_to_process, desc="Avg. Shortest Path (BFS)", unit="node"):
        distances = bfs_shortest_paths(graph, start_node)
        for target_node, dist_val in distances.items():
            if target_node != start_node:
                total_path_length += dist_val
                num_paths_found += 1
    return total_path_length / num_paths_found if num_paths_found > 0 else 0.0

# --- 2. Detección de Comunidades (Louvain Optimizado) ---

def louvain_optimized(graph, max_passes=5, min_modularity_increase=1e-7):
    """
    Algoritmo de Louvain (Fase 1) optimizado usando cálculo de Delta Q.
    Trata el grafo como NO DIRIGIDO para la modularidad.
    Ref: Blondel et al. (2008) "Fast unfolding of communities in large networks"
    """
    nodes = graph.get_nodes()
    if not nodes: return {}

    # 1. Construir representación no dirigida y calcular grados y m (número de aristas no dirigidas)
    adj_undirected = collections.defaultdict(set)
    degrees_undirected = collections.defaultdict(int)
    edge_set_undirected = set()

    for u in graph.adj: # graph.adj contiene aristas dirigidas
        for v in graph.adj[u]:
            # Considerar la existencia de una arista dirigida u->v como una arista no dirigida (u,v)
            # No añadir duplicados si el grafo original ya tiene u->v y v->u.
            # La lista de adyacencia no dirigida las tendrá en ambos sentidos.
            adj_undirected[u].add(v)
            adj_undirected[v].add(u)

            # Para contar m_undirected correctamente (número de aristas únicas no dirigidas)
            # y calcular grados no dirigidos:
            # No es necesario edge_set_undirected si los grados se calculan desde adj_undirected final.

    # Calcular grados no dirigidos y m_undirected
    for node_id in nodes: # Asegurar que todos los nodos tengan una entrada de grado
        degrees_undirected[node_id] = len(adj_undirected.get(node_id, set()))

    m2_undirected = 0 # Esto será 2*m (suma de todos los grados no dirigidos)
    for node_id in nodes:
        m2_undirected += degrees_undirected[node_id]

    if m2_undirected == 0: # Grafo sin aristas
        return {node: i for i, node in enumerate(nodes)}

    # Inicialización: cada nodo en su propia comunidad
    communities = {node: i for i, node in enumerate(nodes)}

    # Información por comunidad para cálculo de Delta Q:
    # Sigma_tot[c]: Suma de grados (no dirigidos) de nodos en la comunidad c. (ponderado por 2m si se usa esa modularidad)
    # k_i_in[c]: Suma de pesos (1 para no ponderado) de aristas de nodo i a la comunidad c.

    # Sigma_tot[comm_id] = sum of degrees of nodes in community comm_id
    # community_total_degree[c] = sum_{i in c} degree(i)
    community_total_degree = {i: degrees_undirected.get(node,0) for i, node in enumerate(nodes)}

    # Progress bar for Louvain passes
    for current_pass in tqdm(range(max_passes), desc="Louvain Passes", unit="pass"):
        # print(f"Louvain Optimized Pass: {current_pass + 1}") # tqdm handles this
        nodes_shuffled = list(nodes)
        random.shuffle(nodes_shuffled)
        made_change_in_pass = False

        # Optional: Nested progress bar for nodes within a pass
        # Can be verbose for large graphs, leave=False helps clean up after each pass.
        for node_i in tqdm(nodes_shuffled, desc=f"Pass {current_pass + 1}", unit="node", leave=False):
            original_community_id = communities[node_i]
            ki = degrees_undirected.get(node_i, 0)

            # Ganancia de modularidad si node_i se mueve a cada comunidad vecina (o se queda)
            best_target_community_id = original_community_id
            max_delta_q = 0.0 # Ganancia relativa a la comunidad actual de node_i

            # Calcular conectividad de node_i a otras comunidades
            # k_i_to_comm[c] = sum of weights of edges from i to nodes in community c
            k_i_to_comm = collections.defaultdict(float)
            for neighbor in adj_undirected.get(node_i, set()):
                neighbor_comm_id = communities[neighbor]
                k_i_to_comm[neighbor_comm_id] += 1.0 # Peso de arista es 1

            # Considerar quitar node_i de su comunidad actual
            # Efecto en la comunidad original:
            # Sigma_tot'[C_orig] = Sigma_tot[C_orig] - ki
            # k_i_in_C_orig = conectividad de i a su propia comunidad original

            community_total_degree[original_community_id] -= ki # Retirar temporalmente

            candidate_communities_ids = set(k_i_to_comm.keys())
            candidate_communities_ids.add(original_community_id) # Opción de quedarse (o volver)

            for target_comm_id in candidate_communities_ids:
                # Delta Q para mover i a target_comm_id
                # Formula (simplificada de Blondel et al. 2008, eq 2, adaptada):
                # dQ = (k_i,in / 2m) - (Sigma_tot * k_i) / (2m)^2  (Ojo: 2m en denominador)
                # Donde k_i,in es la suma de pesos de aristas de i a la comunidad C (target_comm_id)
                # Sigma_tot es la suma de grados de nodos en C (ANTES de añadir i)
                # k_i es el grado de i.
                # m es el número de aristas no dirigidas (m2_undirected / 2)

                # k_i_in_target: suma de pesos de aristas de i a target_comm_id
                k_i_in_target = k_i_to_comm.get(target_comm_id, 0.0)

                # Sigma_tot_target: suma de grados en target_comm_id (sin contar a i si no estaba ya)
                sigma_tot_target = community_total_degree.get(target_comm_id, 0.0)
                # Si target_comm_id == original_community_id, i ya fue retirado de su Sigma_tot.
                # Si target_comm_id != original_community_id, i no está en sigma_tot_target.

                # Ganancia = [ (k_i_in_target / m2_undirected) - (sigma_tot_target * ki) / (m2_undirected^2) ]
                # El m2_undirected ya es 2*m. La formula es (k_i_in / 2m) - (Sigma_tot * k_i) / (2m)^2
                # Ojo: Blondel et al. usan m para el total de pesos (que es 2*num_aristas para no ponderado)
                # Si usamos m2_undirected = sum of degrees = 2 * num_aristas_no_dirigidas.
                # Entonces Q = sum_ij (Aij - ki*kj / (2m)) * delta(ci,cj)
                # DeltaQ = ( (sum_in + k_i_in) / 2m - ((sum_tot+ki)/2m)^2 ) - ( sum_in/2m - (sum_tot/2m)^2 - (ki/2m)^2 )
                # Esto es para añadir un nodo aislado.
                # Para mover de C_old a C_new, es más complejo.
                # La implementación de NetworkX usa:
                #   gain = k_i_in_target - sigma_tot_target * ki / m2_undirected
                #   (esto es 2m * delta_Q, así que se compara con 0)

                delta_q = (k_i_in_target - (sigma_tot_target * ki) / m2_undirected)
                # Este delta_q es proporcional al cambio real. No es el valor absoluto.
                # Se compara con el delta_q de la comunidad original.

                if delta_q > max_delta_q:
                    max_delta_q = delta_q
                    best_target_community_id = target_comm_id

            # Añadir de nuevo ki a la comunidad de donde se retiró (que podría ser la original o la mejor si no cambió)
            # Si best_target_community_id es diferente, se actualizará después.
            community_total_degree[original_community_id] += ki # Revertir el retiro temporal

            # Si se encontró una mejor comunidad (con mayor ganancia de modularidad)
            if best_target_community_id != original_community_id:
                 # Mover el nodo i
                communities[node_i] = best_target_community_id
                made_change_in_pass = True

                # Actualizar Sigma_tot para las comunidades afectadas
                community_total_degree[original_community_id] -= ki # Quitar de la vieja
                community_total_degree[best_target_community_id] += ki  # Añadir a la nueva

        # current_pass is handled by the tqdm loop for passes
        if not made_change_in_pass:
            tqdm.write(f"  No change in modularity during pass {current_pass + 1}, stopping Louvain Phase 1.")
            break # Stop if no improvement in a pass

    # Fase 2 (agregación de red) no implementada en esta versión.
    return communities


# --- 3. Árbol de Expansión Mínima (Prim) ---
# (Prim MST se mantiene como estaba, ya que su complejidad es aceptable para este ejercicio
#  y el foco principal de optimización de escalabilidad era Louvain)
def prim_mst(graph):
    nodes = graph.get_nodes()
    if not nodes: return []
    undirected_adj = collections.defaultdict(set)
    for u_node in graph.adj:
        for v_node in graph.adj[u_node]:
            undirected_adj[u_node].add(v_node)
            undirected_adj[v_node].add(u_node)

    mst_edges = []
    nodes_in_mst = set()
    start_node_for_mst = None
    for node_candidate in nodes:
        if node_candidate in undirected_adj and undirected_adj[node_candidate]:
            start_node_for_mst = node_candidate
            break
    if start_node_for_mst is None and nodes:
        start_node_for_mst = nodes[0]
    if not start_node_for_mst: return []

    nodes_in_mst.add(start_node_for_mst)
    edge_candidates_heap = []
    for neighbor in undirected_adj.get(start_node_for_mst, []):
        heapq.heappush(edge_candidates_heap, (1, start_node_for_mst, neighbor)) # Peso 1

    processed_edges_in_mst = set() # Para evitar añadir la misma arista dos veces (e.g. (u,v) y (v,u))

    # Progress bar for Prim's algorithm, progressing as nodes are added to MST
    # Total is the number of nodes in the graph. Initial is 1 as start_node_for_mst is already added.
    # Ensure graph.get_number_of_nodes() is efficient or pre-fetched if called repeatedly.
    # Here, it's fine as it's mainly for the total.
    num_total_nodes = graph.get_number_of_nodes()
    # Initialize tqdm after nodes_in_mst has its first node.
    # The loop condition `len(nodes_in_mst) < num_total_nodes` is key.
    # We can update the progress bar each time a node is added.

    prim_progress_bar = tqdm(total=num_total_nodes, desc="Prim MST", unit="node", initial=len(nodes_in_mst))

    while edge_candidates_heap and len(nodes_in_mst) < num_total_nodes:
        weight, u, v = heapq.heappop(edge_candidates_heap)
        if v not in nodes_in_mst:
            nodes_in_mst.add(v)
            prim_progress_bar.update(1) # Increment progress by 1 node

            # Guardar arista en formato canónico (u < v) y asegurar unicidad
            canonical_edge = tuple(sorted((u, v)))
            if canonical_edge not in processed_edges_in_mst:
                 mst_edges.append(canonical_edge)
                 processed_edges_in_mst.add(canonical_edge)

            for neighbor_of_v in undirected_adj.get(v, []):
                if neighbor_of_v not in nodes_in_mst:
                    heapq.heappush(edge_candidates_heap, (1, v, neighbor_of_v))

    prim_progress_bar.close() # Close the progress bar when done
    return sorted(list(processed_edges_in_mst))


# --- Mock SocialGraph para pruebas internas ---
class MockSocialGraph: # (Mantenido como estaba para pruebas)
    def __init__(self):
        self.adj = collections.defaultdict(list)
        self.nodes_set = set()
        self._num_edges = 0
    def add_edge(self, u, v):
        self.adj[u].append(v)
        self.nodes_set.add(u); self.nodes_set.add(v)
        self._num_edges += 1
    def get_nodes(self): return sorted(list(self.nodes_set))
    def get_number_of_nodes(self): return len(self.nodes_set)
    def get_number_of_edges(self): return self._num_edges
    def get_node_degree(self, node_id, degree_type="out"):
        if degree_type == "out": return len(self.adj.get(node_id, []))
        elif degree_type == "in":
            return sum(1 for u_node in self.adj if node_id in self.adj[u_node])
        return 0

# --- Bloque de Pruebas ---
if __name__ == "__main__":
    print("--- Testing Network Algorithms (with Louvain Optimizations) ---")

    # 1. Test BFS y Average Shortest Path Length (sin cambios, se asume que funcionan)
    print("\n--- Testing BFS & Average Shortest Path (Briefly) ---")
    g_bfs = MockSocialGraph()
    g_bfs.add_edge(1, 2); g_bfs.add_edge(1, 3); g_bfs.add_edge(2, 4)
    g_bfs.nodes_set.update([1,2,3,4])
    print("BFS from 1:", bfs_shortest_paths(g_bfs, 1))
    print(f"Avg Shortest Path (g_bfs): {average_shortest_path_length(g_bfs):.3f}")

    # 2. Test Louvain Optimizado
    print("\n--- Testing Louvain Optimized ---")
    g_louvain_test = MockSocialGraph()
    # Comunidad A: 1,2,3. Comunidad B: 4,5,6. Puente 3->4
    # Aristas dirigidas, pero Louvain las tratará como no dirigidas.
    g_louvain_test.add_edge(1,2); g_louvain_test.add_edge(2,1)
    g_louvain_test.add_edge(1,3); g_louvain_test.add_edge(3,1)
    g_louvain_test.add_edge(2,3); g_louvain_test.add_edge(3,2) # Comp. 1
    g_louvain_test.add_edge(4,5); g_louvain_test.add_edge(5,4)
    g_louvain_test.add_edge(4,6); g_louvain_test.add_edge(6,4)
    g_louvain_test.add_edge(5,6); g_louvain_test.add_edge(6,5) # Comp. 2
    g_louvain_test.add_edge(3,4) # Puente C1 -> C2 (efectivamente (3,4) no dirigido para Louvain)
    g_louvain_test.nodes_set.update([1,2,3,4,5,6])

    print(f"Graph for Louvain: Nodes={g_louvain_test.get_nodes()}, Edges (directed)={g_louvain_test.get_number_of_edges()}")

    communities = louvain_optimized(g_louvain_test, max_passes=10)
    print("Detected communities (g_louvain_test):")
    grouped_communities = collections.defaultdict(list)
    if communities:
        for node, comm_id in communities.items():
            grouped_communities[comm_id].append(node)
        for comm_id in sorted(grouped_communities.keys()):
            print(f"  Community {comm_id}: {sorted(grouped_communities[comm_id])}")
    else:
        print("Louvain did not return communities.")

    # Prueba con un grafo más simple para Louvain
    g_simple_louvain = MockSocialGraph()
    g_simple_louvain.add_edge(1,2); g_simple_louvain.add_edge(2,1)
    g_simple_louvain.add_edge(3,4); g_simple_louvain.add_edge(4,3)
    g_simple_louvain.add_edge(1,3) # Puente
    g_simple_louvain.nodes_set.update([1,2,3,4])
    print("\nLouvain with simpler graph (1-2, 3-4, 1-3 bridge):")
    simple_communities = louvain_optimized(g_simple_louvain)
    if simple_communities:
        s_grouped_communities = collections.defaultdict(list)
        for node, comm_id in simple_communities.items():
            s_grouped_communities[comm_id].append(node)
        for comm_id in sorted(s_grouped_communities.keys()):
            print(f"  Community {comm_id}: {sorted(s_grouped_communities[comm_id])}")


    # 3. Test Prim MST (sin cambios, se asume que funciona)
    print("\n--- Testing Prim MST (Briefly) ---")
    g_mst_test = MockSocialGraph()
    g_mst_test.add_edge(1,2); g_mst_test.add_edge(2,3); g_mst_test.add_edge(1,3) # Triángulo
    g_mst_test.nodes_set.update([1,2,3])
    mst_edges = prim_mst(g_mst_test)
    print(f"MST edges (g_mst_test): {mst_edges}") # Esperado 2 aristas, e.g., [(1,2), (1,3)]
