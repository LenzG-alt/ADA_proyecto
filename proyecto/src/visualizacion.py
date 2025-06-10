# visualizacion.py

import networkx as nx
import matplotlib.pyplot as plt

def visualizar_grafo_reducido(grafo, num_nodos_a_mostrar=50):
    """Visualiza una parte pequeña del grafo"""
    G = nx.DiGraph()  # Grafo dirigido según especificaciones

    for u in range(num_nodos_a_mostrar):
        for v in grafo.lista_adyacencia[u]:
            if v < num_nodos_a_mostrar:  # Solo muestra conexiones dentro del subgrafo
                G.add_edge(u, v)

    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, k=0.15, iterations=20)
    nx.draw(G, pos, with_labels=True, node_size=50, font_size=8, arrows=True)
    plt.title("Subgrafo de la red social")
    plt.savefig("resultados/graficos/subgrafo.png")
    plt.show()