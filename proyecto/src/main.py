# main.py
from visualizacion import visualizar_grafo_reducido

from config import DATASET_PATH, MAX_USERS_TO_LOAD
from carga_datos import cargar_usuarios, cargar_ubicaciones
from construccion_grafo import construir_grafo
import eda
from analisis_grafo import detectar_componentes_conexas
import logging
from utils import setup_logger

setup_logger()

if __name__ == "__main__":
    logging.info("Iniciando análisis de la red social X")

    # 1. Cargar datos
    conexiones = cargar_usuarios(DATASET_PATH['usuarios'], MAX_USERS_TO_LOAD)
    ubicaciones = cargar_ubicaciones(DATASET_PATH['ubicaciones'], MAX_USERS_TO_LOAD)

    # 2. Construir grafo
    grafo = construir_grafo(conexiones)
    grafo.mostrar_grafo()

    # 4. Análisis del grafo
    componentes = detectar_componentes_conexas(grafo)
    print(f"Número de componentes conexas: {len(componentes)}")
    print(f"Tamaño de la componente más grande: {max(len(c) for c in componentes)}")

    # 5. Visualización del grafo (opcional)
    visualizar_grafo_reducido(grafo, num_nodos_a_mostrar=100)



    grados_salida, grados_entrada = eda.estadisticas_grado(conexiones)
    eda.graficar_distribucion_grados(grados_salida, grados_entrada)

    outliers_salida = eda.detectar_outliers(grados_salida)
    print(f"Cantidad de outliers en grado de salida: {len(outliers_salida)}")