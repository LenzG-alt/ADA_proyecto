# construccion_grafo.py

class Grafo:
    def __init__(self, num_nodos):
        self.num_nodos = num_nodos
        self.lista_adyacencia = [[] for _ in range(num_nodos)]

    def agregar_arista(self, u, v):
        self.lista_adyacencia[u].append(v)

    def mostrar_grafo(self, limite=10):
        """Muestra solo una parte del grafo para verificación"""
        print("Grafo (primeras conexiones):")
        for i in range(limite):
            print(f"Nodo {i}: {self.lista_adyacencia[i]}")

def construir_grafo(conexiones):
    num_nodos = len(conexiones)
    grafo = Grafo(num_nodos)
    for u, amigos in enumerate(conexiones):
        for v in amigos:
            if v < num_nodos:  # Evita índices fuera de rango
                grafo.agregar_arista(u, v)
    return grafo