# analisis_grafo.py

from collections import deque
import numpy as np

def bfs(grafo, inicio, visitados):
    cola = deque([inicio])
    visitados[inicio] = True
    componente = [inicio]

    while cola:
        nodo = cola.popleft()
        for vecino in grafo.lista_adyacencia[nodo]:
            if not visitados[vecino]:
                visitados[vecino] = True
                cola.append(vecino)
                componente.append(vecino)
    return componente

def detectar_componentes_conexas(grafo):
    visitados = np.zeros(grafo.num_nodos, dtype=bool)  # Uso de numpy para velocidad
    componentes = []

    for nodo in range(grafo.num_nodos):
        if not visitados[nodo]:
            comp = bfs(grafo, nodo, visitados)
            componentes.append(comp)
    return componentes


def encontrar_camino_minimo_bfs(grafo, inicio_id, fin_id):
    """
    Encuentra el camino mínimo entre dos nodos en un grafo usando BFS.

    Args:
        grafo (Grafo): El objeto grafo (de la clase Grafo).
        inicio_id (int): El ID del nodo de inicio.
        fin_id (int): El ID del nodo de fin.

    Returns:
        list of int or None: Una lista de IDs de nodos representando el camino más corto
                             desde inicio_id a fin_id. Retorna [inicio_id] si inicio_id == fin_id.
                             Retorna None si no hay camino, o si los IDs están fuera de rango.
    """
    if not (0 <= inicio_id < grafo.num_nodos and 0 <= fin_id < grafo.num_nodos):
        print(f"Error: IDs de nodo {inicio_id} o {fin_id} fuera de rango (0-{grafo.num_nodos - 1}).")
        return None

    if inicio_id == fin_id:
        return [inicio_id]

    cola = deque([(inicio_id, [inicio_id])])  # Almacena (nodo_actual, camino_hasta_ahora)
    visitados = {inicio_id}  # Conjunto para búsqueda rápida de nodos visitados

    while cola:
        nodo_actual, camino_actual = cola.popleft()

        for vecino in grafo.lista_adyacencia[nodo_actual]:
            if vecino == fin_id:
                return camino_actual + [vecino]

            if vecino not in visitados:
                visitados.add(vecino)
                nuevo_camino = camino_actual + [vecino]
                cola.append((vecino, nuevo_camino))

    print(f"No se encontró camino entre {inicio_id} y {fin_id}.")
    return None
