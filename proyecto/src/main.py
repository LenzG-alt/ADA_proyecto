# main.py
import logging
from tqdm import tqdm # Importar tqdm
from config import DATASET_PATH, MAX_USERS_TO_LOAD as DEFAULT_MAX_USERS
from carga_datos import cargar_usuarios, cargar_ubicaciones
from construccion_grafo import construir_grafo_desde_conexiones, GrafoNX
import eda
import analisis_grafo as ag
import visualizacion as vis
from utils import setup_logger, medir_tiempo
from geografia import graficar_distribucion_geografica
import networkx as nx # Asegurarse de que networkx está importado

# Configurar logger al inicio
setup_logger()

# Variables globales para almacenar los datos cargados y el grafo
conexiones_cargadas = None
ubicaciones_cargadas = None
grafo_networkx_cargado = None
num_usuarios_reales = 0

def mostrar_menu_principal():
    print("\n--- Menú Principal de Análisis de Grafo ---")
    print("1. Cargar Datos")
    print("2. Análisis Exploratorio de Datos (EDA)")
    print("3. Análisis de Componentes Conexas")
    print("4. Métricas de Centralidad")
    print("5. Coeficiente de Clustering")
    print("6. Detección de Comunidades")
    print("7. Caminos Más Cortos")
    print("8. Análisis de Propiedades de Mundo Pequeño")
    print("0. Salir")
    return input("Seleccione una opción: ")

def mostrar_submenu_carga():
    print("\n--- Submenú Cargar Datos ---")
    print("a. Cargar datos completos (10 millones)")
    print("b. Cargar muestra de datos (especificar tamaño)")
    print("z. Volver al menú principal")
    return input("Seleccione una opción: ")

def mostrar_submenu_eda():
    print("\n--- Submenú Análisis Exploratorio de Datos (EDA) ---")
    print("a. Calcular estadísticas de grado")
    print("b. Graficar distribución de grados")
    print("c. Analizar correlación de grados (Entrada/Salida)")
    print("d. Mostrar Top N usuarios por seguidores")
    print("z. Volver al menú principal")
    return input("Seleccione una opción: ")

def mostrar_submenu_centralidad():
    print("\n--- Submenú Métricas de Centralidad ---")
    print("a. Calcular PageRank")
    print("b. Calcular Centralidad de Grado (Entrada/Salida)")
    print("c. Calcular Centralidad de Intermediación (Opcional, costoso)")
    print("d. Calcular Centralidad de Cercanía (Opcional, costoso)")
    print("z. Volver al menú principal")
    return input("Seleccione una opción: ")

def mostrar_submenu_caminos():
    print("\n--- Submenú Caminos Más Cortos ---")
    print("a. Encontrar camino más corto entre dos usuarios")
    print("b. Calcular diámetro de la componente gigante (Opcional, costoso)")
    print("z. Volver al menú principal")
    return input("Seleccione una opción: ")


@medir_tiempo
def manejar_carga_datos(opcion_carga):
    global conexiones_cargadas, ubicaciones_cargadas, grafo_networkx_cargado, num_usuarios_reales
    max_usuarios_a_cargar = 0

    if opcion_carga == 'a':
        max_usuarios_a_cargar = 10000000 # Límite real para "completo"
        logging.info(f"Iniciando carga de datos completos (hasta {max_usuarios_a_cargar} usuarios).")
    elif opcion_carga == 'b':
        while True:
            try:
                muestra = input("Ingrese el número de usuarios para la muestra (ej. 1000): ")
                max_usuarios_a_cargar = int(muestra)
                if max_usuarios_a_cargar > 0:
                    logging.info(f"Iniciando carga de muestra de datos ({max_usuarios_a_cargar} usuarios).")
                    break
                else:
                    print("El tamaño de la muestra debe ser un número positivo.")
            except ValueError:
                print("Entrada no válida. Por favor, ingrese un número.")
    else:
        print("Opción no válida.")
        return

    # Simulación de progreso para carga de datos
    with tqdm(total=2, desc="Cargando datos") as pbar:
        conexiones_cargadas = cargar_usuarios(DATASET_PATH['usuarios'], max_usuarios_a_cargar)
        pbar.update(1)
        ubicaciones_cargadas = cargar_ubicaciones(DATASET_PATH['ubicaciones'], max_usuarios_a_cargar)
        pbar.update(1)

    num_usuarios_reales = len(conexiones_cargadas)
    if num_usuarios_reales == 0:
        logging.error("No se cargaron datos de usuarios.")
        conexiones_cargadas = None # Resetear si falla
        ubicaciones_cargadas = None
        grafo_networkx_cargado = None
        return

    logging.info(f"Datos cargados: {num_usuarios_reales} usuarios con conexiones, {len(ubicaciones_cargadas if ubicaciones_cargadas else [])} ubicaciones.")

    logging.info("Construyendo grafo...")
    # Simulación de progreso para construcción de grafo
    with tqdm(total=1, desc="Construyendo grafo") as pbar_grafo:
        if conexiones_cargadas:
            grafo_nx_wrapper = construir_grafo_desde_conexiones(conexiones_cargadas, num_usuarios_reales)
            grafo_networkx_cargado = grafo_nx_wrapper.obtener_grafo_nx()
            pbar_grafo.update(1)
            logging.info("Grafo construido exitosamente.")
        else:
            grafo_networkx_cargado = nx.DiGraph() # Grafo vacío si no hay conexiones
            pbar_grafo.update(1)
            logging.info("No hay conexiones para construir el grafo. Se crea un grafo vacío.")


def ejecutar_opcion_eda(opcion_eda):
    if not grafo_networkx_cargado or grafo_networkx_cargado.number_of_nodes() == 0:
        print("Por favor, cargue los datos y construya el grafo primero (Opción 1 del menú principal).")
        return

    if opcion_eda == 'a':
        print("Calculando estadísticas de grado...")
        with tqdm(total=1, desc="Calculando estadísticas de grado") as pbar:
            eda.calcular_estadisticas_grado_networkx(grafo_networkx_cargado)
            pbar.update(1)
    elif opcion_eda == 'b':
        print("Graficando distribución de grados...")
        grados_salida, grados_entrada = eda.calcular_estadisticas_grado_networkx(grafo_networkx_cargado) # Necesita los grados
        with tqdm(total=1, desc="Graficando distribución") as pbar:
            eda.graficar_distribucion_grados(grados_salida, grados_entrada)
            pbar.update(1)
    elif opcion_eda == 'c':
        print("Analizando correlación de grados...")
        with tqdm(total=1, desc="Analizando correlación") as pbar:
            eda.analizar_correlacion_grados(grafo_networkx_cargado)
            pbar.update(1)
    elif opcion_eda == 'd':
        while True:
            try:
                n_top = input("Ingrese el número de Top N usuarios a mostrar: ")
                n_top_int = int(n_top)
                if n_top_int > 0:
                    break
                else:
                    print("N debe ser un número positivo.")
            except ValueError:
                print("Entrada no válida. Ingrese un número.")
        print(f"Mostrando Top {n_top_int} usuarios por seguidores (grado de entrada)...")
        grados_entrada_dict = dict(grafo_networkx_cargado.in_degree())
        top_n_seguidores = sorted(grados_entrada_dict.items(), key=lambda item: item[1], reverse=True)[:n_top_int]
        print(f"Top {n_top_int} usuarios por número de seguidores:")
        for i, (usuario, seguidores) in enumerate(top_n_seguidores):
            print(f"{i+1}. Usuario {usuario}: {seguidores} seguidores")
    else:
        print("Opción de EDA no válida.")

def ejecutar_opcion_centralidad(opcion_centralidad):
    if not grafo_networkx_cargado or grafo_networkx_cargado.number_of_nodes() == 0:
        print("Por favor, cargue los datos y construya el grafo primero.")
        return

    if opcion_centralidad == 'a':
        print("Calculando PageRank...")
        with tqdm(total=1, desc="Calculando PageRank") as pbar:
            ag.calcular_metricas_centralidad(grafo_networkx_cargado) # PageRank está dentro
            pbar.update(1)
        print("PageRank calculado. Ver 'resultados/metricas/pagerank.txt' y logs.")
    elif opcion_centralidad == 'b':
        print("Calculando Centralidad de Grado...")
        with tqdm(total=1, desc="Calculando Centralidad de Grado") as pbar:
            # La función de centralidad ya loggea esto, pero podemos ser más explícitos
            grados_salida = dict(grafo_networkx_cargado.out_degree())
            grados_entrada = dict(grafo_networkx_cargado.in_degree())
            logging.info(f"Top 5 por grado de salida: {sorted(grados_salida.items(), key=lambda x: x[1], reverse=True)[:5]}")
            logging.info(f"Top 5 por grado de entrada: {sorted(grados_entrada.items(), key=lambda x: x[1], reverse=True)[:5]}")
            pbar.update(1)
        print("Centralidad de grado calculada y loggeada.")
    # Las siguientes son opcionales y pueden estar comentadas en analisis_grafo.py
    elif opcion_centralidad == 'c':
        print("Calculando Centralidad de Intermediación (puede ser lento)...")
        # Esta función puede no estar completamente implementada o ser muy costosa
        # ag.calcular_metricas_centralidad(grafo_networkx_cargado) # Asumiendo que está allí
        print("Función de Centralidad de Intermediación (si está activa en el código fuente) ejecutada.")
    elif opcion_centralidad == 'd':
        print("Calculando Centralidad de Cercanía (puede ser lento)...")
        # ag.calcular_metricas_centralidad(grafo_networkx_cargado) # Asumiendo que está allí
        print("Función de Centralidad de Cercanía (si está activa en el código fuente) ejecutada.")
    else:
        print("Opción de Centralidad no válida.")

def ejecutar_opcion_caminos(opcion_caminos):
    if not grafo_networkx_cargado or grafo_networkx_cargado.number_of_nodes() == 0:
        print("Por favor, cargue los datos y construya el grafo primero.")
        return

    if opcion_caminos == 'a':
        while True:
            try:
                inicio_str = input("Ingrese ID del usuario de inicio: ")
                inicio = int(inicio_str)
                fin_str = input("Ingrese ID del usuario de fin: ")
                fin = int(fin_str)
                if inicio in grafo_networkx_cargado and fin in grafo_networkx_cargado:
                    break
                else:
                    print("Uno o ambos IDs no existen en el grafo cargado. Intente de nuevo.")
            except ValueError:
                print("Entrada no válida. Ingrese IDs numéricos.")

        print(f"Buscando camino más corto entre usuario {inicio} y {fin}...")
        with tqdm(total=1, desc=f"Calculando camino {inicio}->{fin}") as pbar:
            ag.calcular_caminos_cortos(grafo_networkx_cargado, inicio, fin)
            pbar.update(1)
    elif opcion_caminos == 'b':
        print("Calculando diámetro de la componente gigante (puede ser muy lento)...")
        with tqdm(total=1, desc="Calculando diámetro") as pbar: # Progreso general
            ag.calcular_caminos_cortos(grafo_networkx_cargado) # Llama a la parte del diámetro
            pbar.update(1)
    else:
        print("Opción de Caminos no válida.")


@medir_tiempo
def main_loop():
    global grafo_networkx_cargado # Para acceder y modificar la variable global

    while True:
        opcion = mostrar_menu_principal()

        if opcion == '1':
            sub_opcion_carga = mostrar_submenu_carga()
            if sub_opcion_carga == 'z':
                continue
            manejar_carga_datos(sub_opcion_carga)
        elif opcion == '2':
            if not grafo_networkx_cargado:
                print("Cargue los datos primero (Opción 1).")
                continue
            sub_opcion_eda = mostrar_submenu_eda()
            if sub_opcion_eda == 'z':
                continue
            ejecutar_opcion_eda(sub_opcion_eda)
        elif opcion == '3':
            if not grafo_networkx_cargado: print("Cargue los datos primero."); continue
            print("Analizando componentes fuertemente conexas...")
            with tqdm(total=1, desc="Analizando Componentes Conexas") as pbar:
                ag.analizar_componentes_conexas(grafo_networkx_cargado)
                pbar.update(1)
        elif opcion == '4':
            if not grafo_networkx_cargado: print("Cargue los datos primero."); continue
            sub_opcion_centralidad = mostrar_submenu_centralidad()
            if sub_opcion_centralidad == 'z': continue
            ejecutar_opcion_centralidad(sub_opcion_centralidad)
        elif opcion == '5':
            if not grafo_networkx_cargado: print("Cargue los datos primero."); continue
            print("Calculando coeficiente de clustering...")
            with tqdm(total=1, desc="Calculando Coef. Clustering") as pbar:
                ag.calcular_coeficiente_clustering(grafo_networkx_cargado)
                pbar.update(1)
        elif opcion == '6':
            if not grafo_networkx_cargado: print("Cargue los datos primero."); continue
            print("Detectando comunidades (Louvain)...")
            with tqdm(total=1, desc="Detectando Comunidades") as pbar:
                ag.encontrar_comunidades(grafo_networkx_cargado)
                pbar.update(1)
        elif opcion == '7':
            if not grafo_networkx_cargado: print("Cargue los datos primero."); continue
            sub_opcion_caminos = mostrar_submenu_caminos()
            if sub_opcion_caminos == 'z': continue
            ejecutar_opcion_caminos(sub_opcion_caminos)
        elif opcion == '8':
            if not grafo_networkx_cargado: print("Cargue los datos primero."); continue
            print("Analizando propiedades de mundo pequeño...")
            with tqdm(total=1, desc="Analizando Mundo Pequeño") as pbar:
                ag.analizar_propiedades_mundo_pequeno(grafo_networkx_cargado)
                pbar.update(1)
        elif opcion == '0':
            print("Saliendo del programa.")
            break
        else:
            print("Opción no válida. Intente de nuevo.")
'''
def run_test_sequence():
    """Ejecuta una secuencia de opciones de menú para probar la aplicación."""
    logging.info("--- INICIANDO SECUENCIA DE PRUEBA AUTOMÁTICA ---")

    # 1. Cargar una muestra de datos pequeña
    print("\n[TEST] Cargando muestra de datos (100 usuarios)...")
    manejar_carga_datos('b_test_100') # Opción 'b' modificada para prueba

    if not grafo_networkx_cargado or grafo_networkx_cargado.number_of_nodes() == 0:
        logging.error("[TEST] Falló la carga de datos o el grafo está vacío. Terminando prueba.")
        return

    # 2. Ejecutar algunas opciones de EDA
    print("\n[TEST] Ejecutando opciones de EDA...")
    ejecutar_opcion_eda('a') # Estadísticas de grado
    ejecutar_opcion_eda('d_test_5') # Top 5 seguidores (modificado para prueba)

    # 3. Ejecutar un análisis de componentes conexas
    print("\n[TEST] Analizando componentes conexas...")
    with tqdm(total=1, desc="[TEST] Analizando Componentes Conexas") as pbar:
        ag.analizar_componentes_conexas(grafo_networkx_cargado)
        pbar.update(1)

    # 4. Ejecutar una métrica de centralidad
    print("\n[TEST] Calculando PageRank...")
    ejecutar_opcion_centralidad('a')

    # 5. Calcular coeficiente de clustering
    print("\n[TEST] Calculando Coeficiente de Clustering...")
    with tqdm(total=1, desc="[TEST] Calculando Coef. Clustering") as pbar:
        ag.calcular_coeficiente_clustering(grafo_networkx_cargado)
        pbar.update(1)

    # 6. Encontrar camino más corto (usar IDs que probablemente existan en una muestra de 100)
    print("\n[TEST] Encontrando camino más corto (ej. 0 -> 1)...")
    if 0 in grafo_networkx_cargado and 1 in grafo_networkx_cargado:
         ejecutar_opcion_caminos('a_test_0_1') # Modificado para prueba
    else:
        logging.warning("[TEST] Nodos 0 o 1 no existen en la muestra, omitiendo prueba de camino corto.")

    # 7. Cargar datos completos (simulado con pocos usuarios para prueba rápida)
    # print("\n[TEST] Cargando datos 'completos' (simulado con 200 usuarios)...")
    # manejar_carga_datos('a_test_200') # Opción 'a' modificada para prueba
    # if grafo_networkx_cargado and grafo_networkx_cargado.number_of_nodes() > 0:
    #     print("\n[TEST] Calculando estadísticas de grado para datos 'completos'...")
    #     ejecutar_opcion_eda('a')


    logging.info("--- SECUENCIA DE PRUEBA AUTOMÁTICA COMPLETADA ---")
'''

# Modificaciones para pruebas automáticas dentro de las funciones existentes
# Esto es un poco invasivo, idealmente las funciones de manejo tomarían parámetros
# en lugar de depender de input() directamente.

def manejar_carga_datos(opcion_carga):
    global conexiones_cargadas, ubicaciones_cargadas, grafo_networkx_cargado, num_usuarios_reales
    max_usuarios_a_cargar = 0

    if opcion_carga == 'a':
        max_usuarios_a_cargar = 10000000
        logging.info(f"Iniciando carga de datos completos (hasta {max_usuarios_a_cargar} usuarios).")
    elif opcion_carga == 'b':
        while True:
            try:
                muestra = input("Ingrese el número de usuarios para la muestra (ej. 1000): ")
                max_usuarios_a_cargar = int(muestra)
                if max_usuarios_a_cargar > 0:
                    logging.info(f"Iniciando carga de muestra de datos ({max_usuarios_a_cargar} usuarios).")
                    break
                else:
                    print("El tamaño de la muestra debe ser un número positivo.")
            except ValueError:
                print("Entrada no válida. Por favor, ingrese un número.")
    elif opcion_carga == 'b_test_100': # Para prueba automática
        max_usuarios_a_cargar = 100
        logging.info(f"[TEST] Iniciando carga de muestra de datos ({max_usuarios_a_cargar} usuarios).")
    elif opcion_carga == 'a_test_200': # Para prueba automática de "completos"
        max_usuarios_a_cargar = 200
        logging.info(f"[TEST] Iniciando carga de datos 'completos' simulada ({max_usuarios_a_cargar} usuarios).")
    else:
        print("Opción no válida.")
        return

    with tqdm(total=2, desc="Cargando datos") as pbar:
        conexiones_cargadas = cargar_usuarios(DATASET_PATH['usuarios'], max_usuarios_a_cargar)
        pbar.update(1)
        ubicaciones_cargadas = cargar_ubicaciones(DATASET_PATH['ubicaciones'], max_usuarios_a_cargar)
        pbar.update(1)

    num_usuarios_reales = len(conexiones_cargadas)
    if num_usuarios_reales == 0:
        logging.error("No se cargaron datos de usuarios.")
        conexiones_cargadas = None
        ubicaciones_cargadas = None
        grafo_networkx_cargado = None
        return

    logging.info(f"Datos cargados: {num_usuarios_reales} usuarios con conexiones, {len(ubicaciones_cargadas if ubicaciones_cargadas else [])} ubicaciones.")

    logging.info("Construyendo grafo...")
    with tqdm(total=1, desc="Construyendo grafo") as pbar_grafo:
        if conexiones_cargadas:
            grafo_nx_wrapper = construir_grafo_desde_conexiones(conexiones_cargadas, num_usuarios_reales)
            grafo_networkx_cargado = grafo_nx_wrapper.obtener_grafo_nx()
            pbar_grafo.update(1)
            logging.info("Grafo construido exitosamente.")
        else:
            grafo_networkx_cargado = nx.DiGraph()
            pbar_grafo.update(1)
            logging.info("No hay conexiones para construir el grafo. Se crea un grafo vacío.")

def ejecutar_opcion_eda(opcion_eda):
    if not grafo_networkx_cargado or grafo_networkx_cargado.number_of_nodes() == 0:
        print("Por favor, cargue los datos y construya el grafo primero (Opción 1 del menú principal).")
        return

    if opcion_eda == 'a':
        print("Calculando estadísticas de grado...")
        with tqdm(total=1, desc="Calculando estadísticas de grado") as pbar:
            eda.calcular_estadisticas_grado_networkx(grafo_networkx_cargado)
            pbar.update(1)
    elif opcion_eda == 'b':
        print("Graficando distribución de grados...")
        grados_salida, grados_entrada = eda.calcular_estadisticas_grado_networkx(grafo_networkx_cargado)
        with tqdm(total=1, desc="Graficando distribución") as pbar:
            eda.graficar_distribucion_grados(grados_salida, grados_entrada)
            pbar.update(1)
    elif opcion_eda == 'c':
        print("Analizando correlación de grados...")
        with tqdm(total=1, desc="Analizando correlación") as pbar:
            eda.analizar_correlacion_grados(grafo_networkx_cargado)
            pbar.update(1)
    elif opcion_eda == 'd':
        n_top_int = 5 # Valor por defecto para no pedir input
        while True:
            try:
                n_top_str = input(f"Ingrese el número de Top N usuarios a mostrar (default {n_top_int}): ")
                if not n_top_str: # Si el usuario presiona Enter, usa el default
                    break
                n_top_int = int(n_top_str)
                if n_top_int > 0:
                    break
                else:
                    print("N debe ser un número positivo.")
            except ValueError:
                print("Entrada no válida. Ingrese un número.")
        print(f"Mostrando Top {n_top_int} usuarios por seguidores (grado de entrada)...")
        grados_entrada_dict = dict(grafo_networkx_cargado.in_degree())
        top_n_seguidores = sorted(grados_entrada_dict.items(), key=lambda item: item[1], reverse=True)[:n_top_int]
        print(f"Top {n_top_int} usuarios por número de seguidores:")
        for i, (usuario, seguidores) in enumerate(top_n_seguidores):
            print(f"{i+1}. Usuario {usuario}: {seguidores} seguidores")
    elif opcion_eda == 'd_test_5': # Para prueba automática
        n_top_int = 5
        print(f"[TEST] Mostrando Top {n_top_int} usuarios por seguidores (grado de entrada)...")
        grados_entrada_dict = dict(grafo_networkx_cargado.in_degree())
        top_n_seguidores = sorted(grados_entrada_dict.items(), key=lambda item: item[1], reverse=True)[:n_top_int]
        logging.info(f"[TEST] Top {n_top_int} usuarios por número de seguidores:")
        for i, (usuario, seguidores) in enumerate(top_n_seguidores):
            logging.info(f"[TEST] {i+1}. Usuario {usuario}: {seguidores} seguidores")
    else:
        print("Opción de EDA no válida.")

def ejecutar_opcion_caminos(opcion_caminos):
    if not grafo_networkx_cargado or grafo_networkx_cargado.number_of_nodes() == 0:
        print("Por favor, cargue los datos y construya el grafo primero.")
        return

    inicio, fin = -1, -1 # Valores por defecto inválidos

    if opcion_caminos == 'a':
        while True:
            try:
                inicio_str = input("Ingrese ID del usuario de inicio: ")
                inicio = int(inicio_str)
                fin_str = input("Ingrese ID del usuario de fin: ")
                fin = int(fin_str)
                if inicio in grafo_networkx_cargado and fin in grafo_networkx_cargado:
                    break
                else:
                    print("Uno o ambos IDs no existen en el grafo cargado. Intente de nuevo.")
            except ValueError:
                print("Entrada no válida. Ingrese IDs numéricos.")
    elif opcion_caminos == 'a_test_0_1': # Para prueba
        inicio, fin = 0, 1
        logging.info(f"[TEST] Preparando para buscar camino más corto entre usuario {inicio} y {fin}...")
        if not (inicio in grafo_networkx_cargado and fin in grafo_networkx_cargado):
            logging.warning(f"[TEST] Nodos {inicio} o {fin} no en el grafo. Omitiendo prueba de camino.")
            return
    elif opcion_caminos == 'b':
        print("Calculando diámetro de la componente gigante (puede ser muy lento)...")
        with tqdm(total=1, desc="Calculando diámetro") as pbar:
            ag.calcular_caminos_cortos(grafo_networkx_cargado)
            pbar.update(1)
        return # Salir después de diámetro ya que no usa inicio/fin
    else:
        print("Opción de Caminos no válida.")
        return

    if inicio != -1 and fin != -1: # Si se establecieron IDs válidos
        print(f"Buscando camino más corto entre usuario {inicio} y {fin}...")
        with tqdm(total=1, desc=f"Calculando camino {inicio}->{fin}") as pbar:
            ag.calcular_caminos_cortos(grafo_networkx_cargado, inicio, fin)
            pbar.update(1)


if __name__ == "__main__":
    logging.info("Iniciando aplicación de análisis de red social X.")

    # Para ejecución normal, descomentar main_loop() y comentar run_test_sequence()
    main_loop()

    # Para pruebas automáticas:
    #run_test_sequence()

    logging.info("Aplicación de análisis de red social X completada.")