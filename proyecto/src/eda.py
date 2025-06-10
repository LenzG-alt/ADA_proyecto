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

    print(f"Número total de nodos: {len(conexiones)}")
    print(f"Número total de aristas: {sum(grados_salida)}")
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