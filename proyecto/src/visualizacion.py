# visualizacion.py
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import os
import logging
from utils import medir_tiempo

BASE_GRAFICOS_PATH = "resultados/graficos/visualizaciones_red"

def _preparar_directorio_graficos():
    os.makedirs(BASE_GRAFICOS_PATH, exist_ok=True)

@medir_tiempo
def visualizar_subgrafo_networkx(grafo_nx, num_nodos_a_mostrar=50, nombre_archivo="subgrafo.png", layout='spring'):
    """
    Visualiza una parte pequeña del grafo NetworkX.
    Permite elegir el layout.
    """
    _preparar_directorio_graficos()

    if not isinstance(grafo_nx, (nx.Graph, nx.DiGraph)):
        logging.error("Se requiere un grafo NetworkX (Graph o DiGraph) para visualizar.")
        return

    if grafo_nx.number_of_nodes() == 0:
        logging.info("Grafo vacío, no se puede visualizar.")
        return

    nodos_a_mostrar = list(grafo_nx.nodes())[:num_nodos_a_mostrar]
    subgrafo = grafo_nx.subgraph(nodos_a_mostrar)

    plt.figure(figsize=(12, 10))

    pos = None
    if layout == 'spring':
        pos = nx.spring_layout(subgrafo, k=0.15, iterations=20, seed=42)
    elif layout == 'kamada_kawai':
        pos = nx.kamada_kawai_layout(subgrafo)
    elif layout == 'circular':
        pos = nx.circular_layout(subgrafo)
    else: # Por defecto spring
        pos = nx.spring_layout(subgrafo, seed=42)
        logging.warning(f"Layout '{layout}' no reconocido, usando 'spring'.")

    nx.draw(subgrafo, pos, with_labels=True, node_size=70,
            font_size=9, font_weight='bold',
            arrows=True if subgrafo.is_directed() else False,
            width=0.5, alpha=0.7,
            node_color='skyblue', edge_color='gray')

    plt.title(f"Subgrafo de la Red Social ({num_nodos_a_mostrar} nodos, Layout: {layout})")

    ruta_completa = os.path.join(BASE_GRAFICOS_PATH, nombre_archivo)
    try:
        plt.savefig(ruta_completa)
        logging.info(f"Subgrafo guardado en {ruta_completa}")
    except Exception as e:
        logging.error(f"Error al guardar el subgrafo en {ruta_completa}: {e}")

    plt.close() # Cerrar la figura para liberar memoria

@medir_tiempo
def graficar_distribucion_pagerank(grafo_nx, nombre_archivo="distribucion_pagerank.png"):
    _preparar_directorio_graficos()
    if not grafo_nx.nodes():
        logging.warning("Grafo vacío, no se puede graficar distribución de PageRank.")
        return

    try:
        pagerank_valores = nx.pagerank(grafo_nx)
        valores_pr = list(pagerank_valores.values())

        plt.figure(figsize=(10, 6))
        sns.histplot(valores_pr, bins=50, kde=True, color='purple', log_scale=(False, True))
        plt.title('Distribución de Valores de PageRank (Escala Log-Y)')
        plt.xlabel('PageRank')
        plt.ylabel('Frecuencia (log)')
        ruta_completa = os.path.join(BASE_GRAFICOS_PATH, nombre_archivo)
        plt.savefig(ruta_completa)
        plt.close()
        logging.info(f"Gráfico de distribución de PageRank guardado en {ruta_completa}")
    except Exception as e:
        logging.error(f"Error al calcular o graficar PageRank: {e}")


@medir_tiempo
def visualizar_comunidades(grafo_nx, particion, num_nodos_a_mostrar=100, nombre_archivo="comunidades.png"):
    """
    Visualiza el grafo con nodos coloreados según la partición de comunidades.
    Muestra un subgrafo para mejorar la legibilidad.
    """
    _preparar_directorio_graficos()
    if not grafo_nx.nodes() or not particion:
        logging.warning("Grafo vacío o partición no proporcionada. No se pueden visualizar comunidades.")
        return

    nodos_a_mostrar = list(grafo_nx.nodes())[:num_nodos_a_mostrar]
    subgrafo = grafo_nx.subgraph(nodos_a_mostrar)

    # Obtener colores para las comunidades del subgrafo
    colores_nodos = []
    comunidades_subgrafo = []
    for nodo in subgrafo.nodes():
        comm_id = particion.get(nodo, -1) # -1 para nodos sin comunidad asignada (no debería pasar si particion es completa)
        colores_nodos.append(comm_id)
        comunidades_subgrafo.append(comm_id)

    num_comunidades_en_subgrafo = len(set(comunidades_subgrafo))

    plt.figure(figsize=(15, 12))
    pos = nx.spring_layout(subgrafo, k=0.2, iterations=25, seed=42)

    cmap = plt.cm.get_cmap('viridis', max(1, num_comunidades_en_subgrafo)) # Colormap

    nx.draw(subgrafo, pos, node_color=colores_nodos, cmap=cmap,
            with_labels=False, node_size=50, width=0.3, alpha=0.7,
            arrows=True if subgrafo.is_directed() else False, edge_color='silver')

    plt.title(f"Visualización de Comunidades en Subgrafo ({num_comunidades_en_subgrafo} comunidades mostradas)")

    # Añadir una leyenda o información sobre colores si es factible (puede ser complejo con muchas comunidades)
    # Ejemplo simple si hay pocas comunidades:
    # if num_comunidades_en_subgrafo < 10:
    #     handles = [plt.Rectangle((0,0),1,1, color=cmap(i)) for i in range(num_comunidades_en_subgrafo)]
    #     labels = [f"Com. {i}" for i in range(num_comunidades_en_subgrafo)]
    #     plt.legend(handles, labels, title="Comunidades")

    ruta_completa = os.path.join(BASE_GRAFICOS_PATH, nombre_archivo)
    try:
        plt.savefig(ruta_completa)
        logging.info(f"Visualización de comunidades guardada en {ruta_completa}")
    except Exception as e:
        logging.error(f"Error al guardar visualización de comunidades: {e}")
    plt.close()