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