import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

def estadisticas_grado(conexiones):
    grados_salida = [len(lst) for lst in conexiones]
    grados_entrada = [0] * len(conexiones)

    # Calcular grado de entrada
    for idx, amigos in enumerate(conexiones):
        for amigo in amigos:
            if amigo < len(grados_entrada):
                grados_entrada[amigo] += 1

    num_nodos = len(conexiones)
    num_aristas = sum(grados_salida)

    print(f"Número total de nodos: {num_nodos}")
    print(f"Número total de aristas: {num_aristas}")

    if num_nodos > 1:
        densidad = num_aristas / (num_nodos * (num_nodos - 1))
        print(f"Densidad de la red: {densidad:.4f}")
    else:
        print("Densidad de la red: N/A (se requiere más de 1 nodo para calcular)")

    print(f"Grado promedio salida: {np.mean(grados_salida):.2f}")
    print(f"Grado promedio entrada: {np.mean(grados_entrada):.2f}")
    print(f"Máximo grado salida: {max(grados_salida)}")
    print(f"Máximo grado entrada: {max(grados_entrada)}")

    return grados_salida, grados_entrada


def graficar_distribucion_grados(grados_salida, grados_entrada):
    os.makedirs("resultados/graficos", exist_ok=True)

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    sns.histplot(grados_salida, bins=50, kde=True, color="blue")
    plt.title("Distribución Grado de Salida")
    plt.xlabel("Grado de Salida")
    plt.ylabel("Frecuencia")

    plt.subplot(1, 2, 2)
    sns.histplot(grados_entrada, bins=50, kde=True, color="green")
    plt.title("Distribución Grado de Entrada")
    plt.xlabel("Grado de Entrada")
    plt.tight_layout()
    plt.savefig("resultados/graficos/distribucion_grados_entrada_salida.png")
    plt.show()


def detectar_outliers(datos):
    q1, q3 = np.percentile(datos, [25, 75])
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = [x for x in datos if x < lower_bound or x > upper_bound]
    return outliers


def calcular_in_grados(conexiones):
    """
    Calcula los in-grados para cada nodo en el grafo.
    Un in-grado de un nodo es el número de aristas que apuntan hacia él.

    Args:
        conexiones (list of list of int): Lista de adyacencia que representa el grafo.
                                         conexiones[i] es una lista de nodos a los que el nodo i está conectado.

    Returns:
        list of int: Una lista donde el índice i contiene el in-grado del nodo i.
    """
    num_nodos = len(conexiones)
    in_grados = [0] * num_nodos
    for u in range(num_nodos):
        for v in conexiones[u]:
            if v < num_nodos:  # Asegurarse de que el amigo es un nodo válido
                in_grados[v] += 1
    return in_grados


def top_n_usuarios_por_seguidores(conexiones, in_grados, n):
    """
    Identifica los N usuarios con más seguidores (mayor in-grado).

    Args:
        conexiones (list of list of int): Lista de adyacencia (usada para obtener el número de usuarios).
                                         Alternativamente, se podría pasar solo el número de usuarios.
        in_grados (list of int): Lista de in-grados para cada usuario.
        n (int): El número de usuarios top a retornar.

    Returns:
        list of tuple: Una lista de tuplas (user_id, follower_count) para los top N usuarios,
                       ordenada por follower_count en orden descendente.
    """
    num_usuarios = len(conexiones)
    if num_usuarios == 0:
        return []

    # Crear lista de tuplas (user_id, follower_count)
    usuarios_con_seguidores = []
    for user_id in range(num_usuarios):
        usuarios_con_seguidores.append((user_id, in_grados[user_id]))

    # Ordenar la lista en orden descendente basado en follower_count
    # En caso de empate en follower_count, el orden entre esos usuarios no está especificado,
    # por lo que se mantiene el orden original relativo (estable).
    usuarios_con_seguidores.sort(key=lambda x: x[1], reverse=True)

    # Retornar los top N usuarios
    return usuarios_con_seguidores[:n]
