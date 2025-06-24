# eda.py
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import networkx as nx
import os
import logging
from utils import medir_tiempo
from tqdm import tqdm

BASE_GRAFICOS_PATH = "resultados/graficos/eda"

def _preparar_directorio_graficos():
    os.makedirs(BASE_GRAFICOS_PATH, exist_ok=True)

@medir_tiempo
def calcular_estadisticas_grado_networkx(grafo_nx):
    """
    Calcula estadísticas de grado utilizando un grafo NetworkX.
    """
    if not grafo_nx.nodes():
        logging.warning("Grafo vacío, no se pueden calcular estadísticas de grado.")
        return [], []

    grados_salida_dict = dict(grafo_nx.out_degree())
    grados_entrada_dict = dict(grafo_nx.in_degree())

    grados_salida = list(grados_salida_dict.values())
    grados_entrada = list(grados_entrada_dict.values())

    # Asegurarse de que todos los nodos estén representados, incluso si tienen grado 0
    # (NetworkX out_degree/in_degree ya lo hace si los nodos fueron añadidos previamente)
    # Si no, se podría hacer:
    # num_nodos = grafo_nx.number_of_nodes()
    # grados_salida = [grados_salida_dict.get(n, 0) for n in grafo_nx.nodes()]
    # grados_entrada = [grados_entrada_dict.get(n, 0) for n in grafo_nx.nodes()]


    logging.info(f"Número total de nodos: {grafo_nx.number_of_nodes()}")
    logging.info(f"Número total de aristas: {grafo_nx.number_of_edges()}")

    if grados_salida:
        logging.info(f"Grado promedio salida: {np.mean(grados_salida):.2f}")
        logging.info(f"Máximo grado salida: {np.max(grados_salida)}")
        logging.info(f"Mínimo grado salida: {np.min(grados_salida)}")
    if grados_entrada:
        logging.info(f"Grado promedio entrada: {np.mean(grados_entrada):.2f}")
        logging.info(f"Máximo grado entrada: {np.max(grados_entrada)}")
        logging.info(f"Mínimo grado entrada: {np.min(grados_entrada)}")

    return grados_salida, grados_entrada

@medir_tiempo
def graficar_distribucion_grados(grados_salida, grados_entrada, nombre_archivo="distribucion_grados.png"):
    _preparar_directorio_graficos()

    if not grados_salida and not grados_entrada:
        logging.warning("No hay datos de grado para graficar.")
        return

    plt.figure(figsize=(14, 6))

    if grados_salida:
        plt.subplot(1, 2, 1)
        sns.histplot(grados_salida, bins=50, kde=False, color="blue", log_scale=(False, True)) # Escala log en Y
        plt.title("Distribución Grado de Salida (Escala Log-Y)")
        plt.xlabel("Grado de Salida")
        plt.ylabel("Frecuencia (log)")
    else:
        plt.subplot(1, 2, 1)
        plt.text(0.5, 0.5, "No hay datos de grado de salida", ha='center', va='center')
        plt.title("Distribución Grado de Salida")


    if grados_entrada:
        plt.subplot(1, 2, 2)
        sns.histplot(grados_entrada, bins=50, kde=False, color="green", log_scale=(False, True)) # Escala log en Y
        plt.title("Distribución Grado de Entrada (Escala Log-Y)")
        plt.xlabel("Grado de Entrada")
        plt.ylabel("Frecuencia (log)")
    else:
        plt.subplot(1, 2, 2)
        plt.text(0.5, 0.5, "No hay datos de grado de entrada", ha='center', va='center')
        plt.title("Distribución Grado de Entrada")

    plt.tight_layout()
    plt.savefig(os.path.join(BASE_GRAFICOS_PATH, nombre_archivo))
    plt.close()
    logging.info(f"Gráfico de distribución de grados guardado en {os.path.join(BASE_GRAFICOS_PATH, nombre_archivo)}")

@medir_tiempo
def detectar_outliers_grado(grados, tipo_grado="salida"):
    if not grados:
        logging.warning(f"No hay datos de grado de {tipo_grado} para detectar outliers.")
        return []

    # El cálculo de percentiles y límites es rápido.
    q1, q3 = np.percentile(grados, [25, 75])
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    # El bucle para encontrar outliers podría beneficiarse de tqdm si 'grados' es muy grande.
    outliers = []
    for x in tqdm(grados, desc=f"Detectando outliers en grado {tipo_grado}", leave=False):
        if x < lower_bound or x > upper_bound:
            outliers.append(x)

    logging.info(f"Detectados {len(outliers)} outliers en grado de {tipo_grado} (Límite sup: {upper_bound:.2f}, Inf: {lower_bound:.2f})")
    return outliers

@medir_tiempo
def analizar_correlacion_grados(grafo_nx):
    """Analiza la correlación entre el grado de entrada y salida de los nodos."""
    if not grafo_nx.nodes() or not isinstance(grafo_nx, nx.DiGraph):
        logging.warning("Se requiere un grafo dirigido con nodos para analizar correlación de grados.")
        return

    grados_entrada = dict(grafo_nx.in_degree())
    grados_salida = dict(grafo_nx.out_degree())

    nodos_comunes = list(set(grados_entrada.keys()) & set(grados_salida.keys()))

    if not nodos_comunes:
        logging.warning("No hay nodos comunes para calcular correlación de grados.")
        return

    # Estos bucles podrían ser largos si hay muchos nodos_comunes.
    entrada_valores = [grados_entrada[n] for n in tqdm(nodos_comunes, desc="Preparando grados de entrada", leave=False)]
    salida_valores = [grados_salida[n] for n in tqdm(nodos_comunes, desc="Preparando grados de salida", leave=False)]

    if len(entrada_valores) < 2 or len(salida_valores) < 2: # np.corrcoef necesita al menos 2 puntos
        logging.warning("No hay suficientes datos para calcular la correlación de grados.")
        return

    correlacion = np.corrcoef(entrada_valores, salida_valores)[0, 1]
    logging.info(f"Coeficiente de correlación entre grado de entrada y salida: {correlacion:.4f}")

    # Graficar correlación (opcional, puede ser denso)
    _preparar_directorio_graficos()
    plt.figure(figsize=(8, 6))
    # Usar una muestra si hay demasiados puntos para que el scatter plot sea legible
    muestra_max = 5000
    if len(nodos_comunes) > muestra_max:
        indices_muestra = np.random.choice(len(nodos_comunes), muestra_max, replace=False)
        entrada_muestra = [entrada_valores[i] for i in indices_muestra]
        salida_muestra = [salida_valores[i] for i in indices_muestra]
    else:
        entrada_muestra = entrada_valores
        salida_muestra = salida_valores

    plt.scatter(entrada_muestra, salida_muestra, alpha=0.3, s=10) # s para tamaño del punto
    plt.title(f'Correlación Grado Entrada vs. Salida (Cor: {correlacion:.2f})')
    plt.xlabel('Grado de Entrada')
    plt.ylabel('Grado de Salida')
    plt.xscale('log') # Escalas logarítmicas pueden ayudar si la distribución es sesgada
    plt.yscale('log')
    plt.grid(True, which="both", ls="-", alpha=0.5)
    plt.savefig(os.path.join(BASE_GRAFICOS_PATH, "correlacion_grados.png"))
    plt.close()
    logging.info(f"Gráfico de correlación de grados guardado.")

    return correlacion

@medir_tiempo
def realizar_eda_completo(grafo_nx, conexiones, ubicaciones):
    """
    Función principal para ejecutar todo el Análisis Exploratorio de Datos.
    'conexiones' se pasa por si alguna función de EDA aún la necesita,
    pero idealmente se usaría grafo_nx.
    """
    logging.info("--- Iniciando EDA General del Grafo ---")

    # Estadísticas y distribución de grados
    grados_salida, grados_entrada = calcular_estadisticas_grado_networkx(grafo_nx)
    if grados_salida or grados_entrada:
        graficar_distribucion_grados(grados_salida, grados_entrada)
        detectar_outliers_grado(grados_salida, "salida")
        detectar_outliers_grado(grados_entrada, "entrada")
        analizar_correlacion_grados(grafo_nx)

    # Podrían añadirse aquí más análisis de EDA según el PDF, como:
    # - Análisis de densidad (ya se muestra en construir_grafo)
    # - Estadísticas sobre atributos de nodos/aristas (si los hubiera)
    # - Análisis de ubicaciones (ya está en geografia.py, se llama desde main)

    logging.info("--- EDA General del Grafo Completado ---")