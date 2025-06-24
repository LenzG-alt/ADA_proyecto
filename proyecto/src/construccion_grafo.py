# construccion_grafo.py
import networkx as nx
from utils import medir_tiempo
import logging

class GrafoNX:
    def __init__(self, dirigido=True):
        if dirigido:
            self.grafo = nx.DiGraph()
        else:
            self.grafo = nx.Graph()
        logging.info(f"Grafo NetworkX {'dirigido' if dirigido else 'no dirigido'} inicializado.")

    def agregar_arista(self, u, v, **attrs):
        self.grafo.add_edge(u, v, **attrs)

    def agregar_nodo(self, nodo, **attrs):
        self.grafo.add_node(nodo, **attrs)

    def obtener_num_nodos(self):
        return self.grafo.number_of_nodes()

    def obtener_num_aristas(self):
        return self.grafo.number_of_edges()

    def obtener_nodos(self):
        return list(self.grafo.nodes())

    def obtener_aristas(self):
        return list(self.grafo.edges(data=True))

    def obtener_adyacencia(self, nodo):
        # En NetworkX, para DiGraph, G.adj[nodo] o G.succ[nodo] da sucesores, G.pred[nodo] da predecesores
        # Para Grafo no dirigido, G.adj[nodo] da vecinos
        return list(self.grafo.adj[nodo])

    def obtener_grafo_nx(self):
        """Devuelve el objeto grafo de NetworkX subyacente."""
        return self.grafo

    def mostrar_info_basica(self):
        num_nodos = self.obtener_num_nodos()
        num_aristas = self.obtener_num_aristas()
        logging.info(f"Información básica del grafo:")
        logging.info(f"  Número de nodos: {num_nodos}")
        logging.info(f"  Número de aristas: {num_aristas}")
        if num_nodos > 0 and isinstance(self.grafo, (nx.Graph, nx.DiGraph)): # nx.density solo para estos tipos
            try:
                densidad = nx.density(self.grafo)
                logging.info(f"  Densidad del grafo: {densidad:.6f}")
            except Exception as e:
                logging.warning(f"No se pudo calcular la densidad: {e}")
        else:
            logging.info("  Densidad del grafo: N/A (grafo vacío o tipo no soportado para densidad)")


@medir_tiempo
def construir_grafo_desde_conexiones(conexiones, num_total_usuarios_en_dataset):
    """
    Construye un grafo dirigido utilizando NetworkX a partir de una lista de conexiones.
    Cada usuario es un nodo, y una conexión de u a v es una arista dirigida.
    'conexiones' es una lista donde el índice 'u' representa el ID del usuario,
    y conexiones[u] es una lista de IDs de usuarios a los que 'u' sigue.
    'num_total_usuarios_en_dataset' es el número total de usuarios que se espera existan,
    basado en MAX_USERS_TO_LOAD o el tamaño total del dataset original si es relevante.
    """
    num_usuarios_cargados = len(conexiones) # Usuarios para los que tenemos datos de conexión
    logging.info(f"Iniciando construcción de grafo con NetworkX. Usuarios con datos de conexión: {num_usuarios_cargados}. Total de nodos a considerar en el grafo: {num_total_usuarios_en_dataset}.")

    g_nx = GrafoNX(dirigido=True)

    # Añadir todos los nodos esperados. Esto es importante si 'num_total_usuarios_en_dataset'
    # representa el universo de usuarios, incluyendo aquellos que podrían no tener conexiones
    # salientes o entrantes dentro del subconjunto de 'conexiones'.
    for i in range(num_total_usuarios_en_dataset):
        g_nx.agregar_nodo(i)

    for u, amigos in enumerate(conexiones):
        # 'u' es el ID del usuario origen (0 hasta num_usuarios_cargados - 1)
        # Verificamos que 'u' esté dentro del rango de nodos definidos para el grafo
        if u < num_total_usuarios_en_dataset:
            for v in amigos:
                # 'v' es el ID del usuario destino
                # Validar que el nodo v también esté dentro del rango de nodos definidos.
                if v < num_total_usuarios_en_dataset:
                    g_nx.agregar_arista(u, v)
                # else:
                #     logging.warning(f"Usuario {u} sigue a {v}, pero el usuario {v} ({v}) está fuera del rango total de usuarios ({num_total_usuarios_en_dataset}). Arista no añadida.")
        # else:
            # Esto no debería ocurrir si 'conexiones' se genera correctamente hasta num_usuarios_cargados
            # y num_usuarios_cargados <= num_total_usuarios_en_dataset
            # logging.warning(f"Usuario {u} está fuera del rango total de usuarios ({num_total_usuarios_en_dataset}). Conexiones no añadidas.")

    g_nx.mostrar_info_basica()
    return g_nx