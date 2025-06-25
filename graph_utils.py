# graph_utils.py
import collections
import time # Para medir tiempos de carga
import os # Para limpiar archivos de prueba en __main__
from tqdm import tqdm

class SocialGraph:
    def __init__(self):
        self.adj = collections.defaultdict(list)
        self.locations = {}  # user_id -> (lat, lon)
        self.num_nodes = 0 # Fuente principal de verdad para el número de nodos
        self.num_edges = 0
        self.in_degrees = None # Para grados de entrada precalculados

    def _process_location_line(self, line, user_id_counter):
        try:
            lat_str, lon_str = line.strip().split(',')
            lat = float(lat_str)
            lon = float(lon_str)
            self.locations[user_id_counter] = (lat, lon)
            return True
        except ValueError:
            # print(f"Warning: Skipping malformed location line (ID ~{user_id_counter}): {line.strip()}")
            return False

    def load_locations_batched(self, location_file, batch_size=100000):
        """
        Carga las ubicaciones de los usuarios desde un archivo en lotes.
        user_id es implícito por el número de línea (1-indexed).
        Establece self.num_nodes basado en el número de líneas en este archivo.
        """
        print(f"Loading locations from {location_file} (batch size: {batch_size})...")
        start_load_time = time.time()
        processed_lines_count = 0
        user_id_implicit_counter = 0

        try:
            # Get total lines for tqdm if possible (requires reading the file once for count)
            try:
                with open(location_file, 'r') as f_count:
                    total_lines = sum(1 for _ in f_count)
            except Exception:
                total_lines = None # Fallback if count fails

            with open(location_file, 'r') as f:
                batch_lines_to_process = []
                # Use unit='loc' for locations, disable if total_lines is None to avoid incorrect percentage
                progress_bar_loc = tqdm(f, total=total_lines, desc="Loading locations", unit="loc", disable=total_lines is None)
                for line_content in progress_bar_loc:
                    user_id_implicit_counter += 1
                    batch_lines_to_process.append((line_content, user_id_implicit_counter))

                    if len(batch_lines_to_process) >= batch_size:
                        for l_content, uid in batch_lines_to_process:
                            self._process_location_line(l_content, uid)
                        processed_lines_count += len(batch_lines_to_process)
                        batch_lines_to_process = []

                if batch_lines_to_process: # Procesar el último lote
                    for l_content, uid in batch_lines_to_process:
                        self._process_location_line(l_content, uid)
                    processed_lines_count += len(batch_lines_to_process)

            # self.num_nodes se establece por el número total de líneas en el archivo de ubicaciones,
            # asumiendo que cada línea corresponde a un ID de usuario secuencial.
            self.num_nodes = user_id_implicit_counter

            end_load_time = time.time()
            # tqdm will print its own summary, so these can be simplified or removed
            print(f"Loaded {len(self.locations)} valid user locations (from {processed_lines_count} lines read).")
            print(f"Number of nodes set to {self.num_nodes} (based on lines in location file).")
            print(f"Location loading time: {end_load_time - start_load_time:.2f} seconds.")

        except FileNotFoundError:
            print(f"Error: Location file {location_file} not found. self.num_nodes remains {self.num_nodes}.")
        except Exception as e:
            print(f"An error occurred during location loading: {e}")

    def _process_user_connection_line(self, line_content, user_id_from):
        connections_str = line_content.strip()
        if not connections_str:
            return 0 # Línea vacía, sin conexiones para este usuario

        edges_added_this_line = 0
        try:
            connected_users_ids = [int(uid_str) for uid_str in connections_str.split(',')]

            # Validar user_id_from (el que origina las conexiones)
            if self.num_nodes > 0 and (user_id_from <= 0 or user_id_from > self.num_nodes):
                # print(f"Warning: User ID {user_id_from} (from connections file) is out of range [1, {self.num_nodes}]. Its connections ignored.")
                return 0

            for user_id_to in connected_users_ids:
                # Validar user_id_to (el destino de la conexión)
                if self.num_nodes > 0 and (user_id_to <= 0 or user_id_to > self.num_nodes):
                    # print(f"Warning: Connection from {user_id_from} to invalid/out-of-range user ID {user_id_to}. Skipped.")
                    continue

                if user_id_from == user_id_to: # Evitar auto-bucles
                    # print(f"Warning: Self-loop for user {user_id_from} ignored.")
                    continue

                self.adj[user_id_from].append(user_id_to)
                edges_added_this_line += 1
            return edges_added_this_line
        except ValueError:
            # print(f"Warning: Malformed connection data for user {user_id_from} (line: '{line_content.strip()}'). Skipped line.")
            return 0

    def load_users_connections_batched(self, user_file, batch_size_progress_report=100000):
        """
        Carga las conexiones de los usuarios línea por línea.
        user_id_from es implícito por el número de línea (1-indexed).
        Si self.num_nodes no fue establecido por load_locations, se inferirá aquí.
        """
        print(f"Loading user connections from {user_file} (progress report every {batch_size_progress_report} lines)...")
        start_load_time = time.time()
        processed_lines_count = 0
        user_id_implicit_counter = 0
        max_user_id_seen_overall = self.num_nodes # Empezar con el num_nodes de las ubicaciones

        try:
            # Get total lines for tqdm
            try:
                with open(user_file, 'r') as f_count:
                    total_lines_usr = sum(1 for _ in f_count)
            except Exception:
                total_lines_usr = None

            with open(user_file, 'r') as f:
                progress_bar_usr = tqdm(f, total=total_lines_usr, desc="Loading user connections", unit="conn", disable=total_lines_usr is None)
                for line_content in progress_bar_usr:
                    user_id_implicit_counter += 1
                    max_user_id_seen_overall = max(max_user_id_seen_overall, user_id_implicit_counter)

                    edges_added = self._process_user_connection_line(line_content, user_id_implicit_counter)
                    self.num_edges += edges_added
                    processed_lines_count += 1

                    # tqdm handles progress reporting, so the explicit batch_size_progress_report log can be removed
                    # if processed_lines_count % batch_size_progress_report == 0:
                    #     pass

            # Si self.num_nodes no fue establecido por ubicaciones (es 0), o si las conexiones
            # implican IDs de nodo más altos que los vistos en ubicaciones.
            if self.num_nodes == 0: # No se cargaron ubicaciones, o el archivo de ubicaciones estaba vacío.
                print("Number of nodes was not set by locations. Inferring from connections file...")
                # Necesitamos encontrar el ID de nodo más alto mencionado en CUALQUIER LUGAR.
                # Esto incluye claves en self.adj y valores en las listas de self.adj.
                # user_id_implicit_counter da el número de líneas en user_file.
                # max_user_id_seen_overall ya rastrea los IDs de origen.
                # Ahora chequear los IDs de destino.
                if self.adj: # Si se añadieron conexiones
                    max_target_id = 0
                    for targets in self.adj.values():
                        if targets:
                            max_target_id = max(max_target_id, max(targets))
                    max_user_id_seen_overall = max(max_user_id_seen_overall, max_target_id)

                self.num_nodes = max_user_id_seen_overall
                print(f"Number of nodes inferred to be {self.num_nodes} based on connections.")
            elif max_user_id_seen_overall > self.num_nodes:
                 # Esto puede ocurrir si el archivo de conexiones hace referencia a IDs de usuario
                 # más allá de lo que estaba en el archivo de ubicaciones.
                 # Por ahora, mantenemos self.num_nodes de las ubicaciones si se cargaron,
                 # las conexiones a IDs mayores son ignoradas por _process_user_connection_line.
                 # Si quisiéramos expandir self.num_nodes:
                 # print(f"Warning: Max user ID in connections ({max_user_id_seen_overall}) > num_nodes from locations ({self.num_nodes}).")
                 # self.num_nodes = max_user_id_seen_overall # Descomentar para permitir expansión
                 pass


            end_load_time = time.time()
            print(f"Processed {processed_lines_count} user connection lines. Total edges accumulated: {self.num_edges}.")
            print(f"Number of nodes (final): {self.get_number_of_nodes(force_recount=False)}.") # Usar el valor cacheado/establecido
            print(f"User connection loading time: {end_load_time - start_load_time:.2f} seconds.")

        except FileNotFoundError:
            print(f"Error: User connections file {user_file} not found.")
        except Exception as e:
            print(f"An error occurred during user connection loading: {e}")

    def get_nodes(self):
        """
        Retorna una lista de todos los IDs de nodos en el grafo (1 a self.num_nodes).
        Asume que los IDs de nodo son contiguos y 1-indexados.
        """
        if self.num_nodes > 0:
            return list(range(1, self.num_nodes + 1))
        return [] # Si num_nodes no está establecido o es 0.

    def get_number_of_nodes(self, force_recount=False):
        """
        Retorna el número de nodos. Prioriza self.num_nodes.
        Si force_recount es True, recalcula desde self.adj (costoso).
        """
        if not force_recount and self.num_nodes > 0:
            return self.num_nodes

        # Recalcular si forzado o si num_nodes es 0 (debería haberse establecido durante la carga)
        if not self.adj:
            self.num_nodes = 0 # Cache
            return 0

        # Esto es un fallback costoso y no debería ser necesario si la carga funciona bien.
        print("Warning: Recalculating number of nodes from adjacency list (costly).")
        max_id = 0
        if self.adj.keys():
            max_id = max(max_id, max(self.adj.keys()))
        for connections_list in self.adj.values():
            if connections_list:
                max_id = max(max_id, max(connections_list))
        self.num_nodes = max_id # Asume que los IDs son hasta el máximo visto.
        return self.num_nodes

    def get_number_of_edges(self):
        return self.num_edges

    def get_node_degree(self, user_id, degree_type="out"):
        # Esta función es llamada por la versión precalculada si existe.
        if degree_type == "out":
            return len(self.adj.get(user_id, []))
        elif degree_type == "in":
            # Si in_degrees no fue precalculado, este es el cálculo costoso.
            if self.in_degrees is not None: # Usar precalculado si existe
                 return self.in_degrees.get(user_id, 0)

            # Cálculo costoso si no precalculado
            in_degree_val = 0
            for source_node_connections in self.adj.values():
                # Contar ocurrencias es más robusto si hay multi-aristas (no debería haber con lista de adyacencia)
                in_degree_val += source_node_connections.count(user_id)
            return in_degree_val
        else:
            raise ValueError("degree_type debe ser 'in' o 'out'")

    def precompute_in_degrees(self):
        """Precalcula y almacena los grados de entrada para todos los nodos."""
        if self.in_degrees is not None:
            print("In-degrees already precomputed.")
            return

        print("Precomputing in-degrees...")
        start_time = time.time()
        self.in_degrees = collections.defaultdict(int)
        for source_node in self.adj: # Iterar sobre nodos que tienen aristas salientes
            for target_node in self.adj[source_node]:
                self.in_degrees[target_node] += 1

        # Asegurar que todos los nodos (de 1 a self.num_nodes) tengan una entrada,
        # incluso si su in-degree es 0. Esto es importante para consistencia.
        if self.num_nodes > 0:
            for i in range(1, self.num_nodes + 1):
                _ = self.in_degrees[i] # Acceder asegura que la clave exista (con valor 0 si no hay aristas entrantes)

        end_time = time.time()
        print(f"In-degree precomputation time: {end_time - start_time:.2f} seconds.")

    def get_average_degree(self, degree_type="out"): # 'degree_type' es nominal aquí
        n_nodes = self.get_number_of_nodes(force_recount=False) # Usar cacheado
        if n_nodes == 0:
            return 0.0
        return self.num_edges / n_nodes

    def ensure_in_degrees_computed(self):
        """
        Asegura que los in-degrees estén calculados. Si no, los calcula.
        """
        if self.in_degrees is None:
            print("In-degrees no calculados. Calculando ahora...")
            self.precompute_in_degrees()
        # else:
            # print("In-degrees ya estaban calculados.") # Opcional: para debugging

    def get_top_n_influencers(self, n=10):
        """
        Retorna los N usuarios más influyentes basados en in-degree.
        Asegura que los in-degrees estén calculados.
        """
        self.ensure_in_degrees_computed()

        if not self.in_degrees: # Si después de asegurar, sigue vacío (e.g., grafo vacío)
            return []

        # Ordenar por in-degree descendente. self.in_degrees es un defaultdict(int).
        # Convertir a lista de tuplas (user_id, in_degree)
        sorted_influencers = sorted(self.in_degrees.items(), key=lambda item: item[1], reverse=True)

        return sorted_influencers[:n]

    def print_graph_summary(self):
        print("\n--- Graph Summary ---")
        num_nodes_val = self.get_number_of_nodes(force_recount=False) # Usar cacheado
        print(f"Number of users (nodes): {num_nodes_val}")
        print(f"Number of connections (edges): {self.get_number_of_edges()}")
        if num_nodes_val > 0:
            avg_deg = self.get_average_degree()
            print(f"Average out-degree (and in-degree): {avg_deg:.2f}")
        else:
            print("Average degree: N/A (no nodes)")

if __name__ == "__main__":
    print("--- Testing Graph Utils with Batched Loading ---")

    test_loc_file = "test_locations.txt"
    test_user_file = "test_users.txt"

    # Contenido de prueba mejorado
    with open(test_loc_file, "w") as f:
        f.write("10.0,10.0\n") # User 1
        f.write("20.0,20.0\n") # User 2
        f.write("30.0,30.0\n") # User 3
        f.write("40.0,40.0\n") # User 4
        f.write("50.0\n")      # User 5 (malformed) -> no se cargará en self.locations
        f.write("60.0,60.0\n") # User 6
        # num_nodes se establecerá en 6 debido a 6 líneas.

    with open(test_user_file, "w") as f:
        f.write("2,3\n")         # User 1 (ID implícito 1) -> 2, 3
        f.write("1\n")           # User 2 -> 1
        f.write("\n")            # User 3 -> (no connections)
        f.write("1,error,5\n")   # User 4 (malformed connection) -> línea ignorada
        f.write("6\n")           # User 5 -> 6. User 5 no tiene ubicación, pero ID 5 es < num_nodes (6).
        f.write("7\n")           # User 6 -> 7. User 7 > num_nodes (6), así que esta arista se ignora.
        f.write("2\n")           # User 7 (ID implícito 7) -> 2. user_id_from 7 > num_nodes (6), conexiones ignoradas.


    graph = SocialGraph()

    print("\n--- Loading Locations (Batched) ---")
    graph.load_locations_batched(test_loc_file, batch_size=2)
    # Esperado: 6 líneas leídas. len(self.locations) = 5. self.num_nodes = 6.

    print("\n--- Loading User Connections (Batched) ---")
    graph.load_users_connections_batched(test_user_file, batch_size_progress_report=2)
    # Aristas esperadas:
    # U1: (1,2), (1,3) -> 2 aristas
    # U2: (2,1) -> 1 arista
    # U3: 0 aristas
    # U4: línea malformada -> 0 aristas
    # U5: (5,6) -> 1 arista (User 5 es < num_nodes, User 6 es < num_nodes)
    # U6: (6,7) -> 0 aristas (User 7 > num_nodes)
    # U7: (línea 7) -> 0 aristas (user_id_from 7 > num_nodes)
    # Total aristas = 2 + 1 + 0 + 0 + 1 + 0 = 4.

    graph.print_graph_summary()
    # Nodos esperados: 6. Aristas: 4.

    print("\n--- Testing In-degree Precomputation ---")
    graph.precompute_in_degrees() # Calcula in_degrees
    # In-degrees esperados:
    # User 1: 1 (de U2)
    # User 2: 1 (de U1)
    # User 3: 1 (de U1)
    # User 4: 0
    # User 5: 0
    # User 6: 1 (de U5)
    # User 7 (y otros no mencionados hasta num_nodes=6): 0
    print(f"In-degree of User 1: {graph.get_node_degree(1, 'in')}")
    print(f"In-degree of User 2: {graph.get_node_degree(2, 'in')}")
    print(f"In-degree of User 3: {graph.get_node_degree(3, 'in')}")
    print(f"In-degree of User 6: {graph.get_node_degree(6, 'in')}")
    print(f"In-degree of User 4: {graph.get_node_degree(4, 'in')}")
    print(f"In-degree of User 5: {graph.get_node_degree(5, 'in')}")
    print(f"Out-degree of User 1: {graph.get_node_degree(1, 'out')}") # Esperado 2
    print(f"Out-degree of User 5: {graph.get_node_degree(5, 'out')}") # Esperado 1

    # Limpiar archivos de prueba
    try:
        os.remove(test_loc_file)
        os.remove(test_user_file)
        print(f"\nCleaned up test files: {test_loc_file}, {test_user_file}")
    except OSError as e:
        print(f"Error cleaning up test files: {e}")
