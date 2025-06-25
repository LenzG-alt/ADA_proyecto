# construccion_grafo.py
import networkx as nx
from tqdm import tqdm
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

    # Añadir todos los nodos esperados de una sola vez.
    # Esto es importante si 'num_total_usuarios_en_dataset'
    # representa el universo de usuarios, incluyendo aquellos que podrían no tener conexiones
    # salientes o entrantes dentro del subconjunto de 'conexiones'.
    logging.info("Añadiendo nodos al grafo...")
    if num_total_usuarios_en_dataset > 0:
        # Envolver add_nodes_from con tqdm si es una operación potencialmente larga,
        # aunque para add_nodes_from(range(N)) es usualmente muy rápido.
        # No obstante, por consistencia y para datasets masivos, podemos hacerlo.
        # Como range() no tiene len() fácil para tqdm sin convertir a lista,
        # y add_nodes_from no devuelve progreso, un tqdm simple sin total es una opción,
        # o podemos asumir que es rápido y no poner tqdm aquí.
        # Por ahora, lo dejamos sin tqdm ya que suele ser instantáneo.
        g_nx.grafo.add_nodes_from(range(num_total_usuarios_en_dataset))
        logging.info(f"{num_total_usuarios_en_dataset} nodos añadidos/asegurados en el grafo.")
    else:
        logging.warning("num_total_usuarios_en_dataset es 0, no se añadirán nodos inicialmente por rango.")

    # Generador para las aristas con tqdm integrado en la iteración del generador
    # Es difícil saber el número total de aristas de antemano sin una pasada previa,
    # así que tqdm aquí no tendrá un 'total' a menos que lo calculemos.
    # Una alternativa es poner tqdm alrededor de la llamada a add_edges_from
    # si el generador se consume progresivamente y add_edges_from lo permite.

    # Estimación del total de aristas para tqdm (opcional, puede ser costoso)
    # total_aristas_estimado = sum(len(amigos) for _, amigos in enumerate(conexiones))
    # logging.info(f"Estimación inicial de aristas a procesar: {total_aristas_estimado}")

    logging.info("Generando y añadiendo aristas al grafo...")

    # Envolveremos el generador con tqdm aquí para seguir el progreso de las aristas generadas.
    # El 'total' podría ser el número de usuarios (conexiones) ya que cada uno genera un lote de aristas.
    # O, si tenemos una estimación del total de aristas, podríamos usar eso.
    # Por simplicidad y eficiencia, usaremos len(conexiones) como total para el progreso de "procesamiento de usuarios para aristas".

    def generar_aristas_con_progreso(conexiones_data, total_usuarios):
        with tqdm(total=len(conexiones_data), desc="Procesando usuarios para aristas", unit="usuarios", disable=logging.getLogger().level > logging.INFO) as pbar_usuarios_aristas:
            for u_idx, amigos_de_u in enumerate(conexiones_data):
                if u_idx < total_usuarios:
                    for v_id in amigos_de_u:
                        if v_id < total_usuarios:
                            yield (u_idx, v_id)
                pbar_usuarios_aristas.update(1)

    # Añadir aristas
    # Si add_edges_from consume el generador de una vez, el tqdm anterior es suficiente.
    # Si add_edges_from lo consume iterativamente, el tqdm dentro del generador es mejor.
    # NetworkX add_edges_from consume el iterable.
    g_nx.grafo.add_edges_from(generar_aristas_con_progreso(conexiones, num_total_usuarios_en_dataset))
    logging.info("Todas las aristas generadas han sido añadidas al grafo.")

    g_nx.mostrar_info_basica()
    return g_nx