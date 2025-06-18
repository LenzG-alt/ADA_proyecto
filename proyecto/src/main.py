# main.py
from visualizacion import visualizar_grafo_reducido
from config import DATASET_PATH, MAX_USERS_TO_LOAD
from carga_datos import cargar_usuarios, cargar_ubicaciones
from construccion_grafo import construir_grafo
import proyecto.src.eda as eda  # Updated import
from proyecto.src.analisis_grafo import detectar_componentes_conexas, encontrar_camino_minimo_bfs # Updated import
from proyecto.src.eda import calcular_in_grados, top_n_usuarios_por_seguidores # Added imports
import logging
from utils import setup_logger

setup_logger()

def obtener_entero(mensaje):
    """Función auxiliar para obtener un entero del usuario."""
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print("Entrada no válida. Por favor, ingrese un número entero.")

if __name__ == "__main__":
    logging.info("Iniciando análisis de la red social X")

    # 1. Cargar datos
    logging.info("Cargando datos...")
    conexiones = cargar_usuarios(DATASET_PATH['usuarios'], MAX_USERS_TO_LOAD)
    # ubicaciones = cargar_ubicaciones(DATASET_PATH['ubicaciones'], MAX_USERS_TO_LOAD) # Descomentar si se usa ubicaciones

    if not conexiones:
        logging.error("No se pudieron cargar las conexiones. Terminando el programa.")
        exit()

    num_total_usuarios = len(conexiones)
    logging.info(f"Datos cargados. Número total de usuarios procesados: {num_total_usuarios}")

    # 2. Construir grafo
    logging.info("Construyendo el grafo...")
    grafo = construir_grafo(conexiones)
    logging.info("Grafo construido.")

    # --- Análisis Pre-Menú ---
    print("\n--- Resumen General del Grafo ---")
    grafo.mostrar_grafo(limite=5) # Mostrar una pequeña parte del grafo

    # grados_salida, grados_entrada = eda.estadisticas_grado(conexiones)
    # # eda.graficar_distribucion_grados(grados_salida, grados_entrada) # Puede ser ruidoso para pre-menu

    # outliers_salida = eda.detectar_outliers(grados_salida)
    # print(f"Cantidad de outliers en grado de salida: {len(outliers_salida)}")
    # outliers_entrada = eda.detectar_outliers(grados_entrada) # Añadido para grados de entrada
    # print(f"Cantidad de outliers en grado de entrada: {len(outliers_entrada)}")

    # componentes = detectar_componentes_conexas(grafo)
    # if componentes:
    #     print(f"Número de componentes conexas: {len(componentes)}")
    #     print(f"Tamaño de la componente más grande: {max(len(c) for c in componentes if c)}")
    # else:
    #     print("No se detectaron componentes conexas (o el grafo está vacío).")
    # print("--- Fin del Resumen General ---\n")

    # --- Menú Interactivo ---
    while True:
        print("\nMenu Principal:")
        print("1. Mostrar estadísticas generales de la red")
        print("2. Visualizar distribuciones de grado")
        print("3. Visualizar subgrafo de la red")
        print("4. Mostrar Top N usuarios por seguidores")
        print("5. Encontrar camino más corto entre dos usuarios")
        print("0. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            print("\n--- Estadísticas Generales de la Red ---")
            # eda.estadisticas_grado ya imprime información básica (nodos, aristas, grado promedio, max grado)
            grados_salida, grados_entrada = eda.estadisticas_grado(conexiones)

            outliers_salida = eda.detectar_outliers(grados_salida)
            print(f"Número de outliers en grado de salida: {len(outliers_salida)}")

            outliers_entrada = eda.detectar_outliers(grados_entrada)
            print(f"Número de outliers en grado de entrada: {len(outliers_entrada)}")

            componentes = detectar_componentes_conexas(grafo)
            if componentes:
                print(f"Número de componentes conexas: {len(componentes)}")
                if any(componentes): # Asegurarse de que hay al menos una componente no vacía
                    tamanos_componentes = [len(c) for c in componentes if c]
                    if tamanos_componentes:
                        print(f"Tamaño de la componente más grande: {max(tamanos_componentes)}")
                    else:
                        print("No hay componentes con nodos.") # Caso raro si componentes no está vacío pero todos son listas vacías
                else: # Si componentes es una lista de listas vacías o solo una lista vacía
                    print("No se encontraron nodos en las componentes.")
            else: # Si componentes es None o una lista vacía
                print("No se detectaron componentes conexas (o el grafo está vacío).")
            print("--- Fin de Estadísticas Generales ---")
        elif opcion == '2':
            print("\n--- Visualización de Distribuciones de Grado ---")
            grados_salida, grados_entrada = eda.estadisticas_grado(conexiones) # También imprime estadísticas
            eda.graficar_distribucion_grados(grados_salida, grados_entrada)
            print("--- Fin de Visualización de Distribuciones de Grado ---")
        elif opcion == '3':
            print("\n--- Visualización de Subgrafo de la Red ---")
            n_subgrafo = obtener_entero("Ingrese el número de nodos a mostrar en el subgrafo (ej. 50 o 100): ")
            if n_subgrafo <= 0:
                print("El número de nodos debe ser un entero positivo.")
            else:
                visualizar_grafo_reducido(grafo, num_nodos_a_mostrar=n_subgrafo)
            print("--- Fin de Visualización de Subgrafo ---")
        elif opcion == '4':
            print("\n--- Top N Usuarios por Seguidores ---")
            n_top = obtener_entero("Ingrese el número de usuarios top a mostrar: ")
            if n_top <= 0:
                print("Por favor, ingrese un número positivo para N.")
            else:
                in_grados = eda.calcular_in_grados(conexiones)
                top_usuarios = eda.top_n_usuarios_por_seguidores(conexiones, in_grados, n_top)

                if top_usuarios:
                    print(f"\nTop {n_top} usuarios con más seguidores:")
                    for i, (user_id, followers) in enumerate(top_usuarios):
                        print(f"{i+1}. Usuario ID: {user_id}, Seguidores: {followers}")
                else:
                    print("No hay usuarios para mostrar o N es inválido.")
            print("--- Fin de Top N Usuarios ---")
        elif opcion == '5':
            print("\n--- Encontrar Camino Más Corto entre Usuarios (BFS) ---")
            id_inicio = obtener_entero(f"Ingrese el ID del usuario de inicio (0-{num_total_usuarios-1}): ")
            id_fin = obtener_entero(f"Ingrese el ID del usuario de destino (0-{num_total_usuarios-1}): ")

            # Validar que los IDs estén dentro del rango posible, aunque encontrar_camino_minimo_bfs también lo hace.
            # Esto es más para dar feedback inmediato si el usuario ingresa algo muy fuera de rango.
            if not (0 <= id_inicio < num_total_usuarios and 0 <= id_fin < num_total_usuarios):
                print("IDs de usuario fuera de rango.")
            else:
                camino = encontrar_camino_minimo_bfs(grafo, id_inicio, id_fin)
                if camino:
                    print("Camino más corto encontrado:")
                    print(" -> ".join(map(str, camino)))
                    print(f"Longitud del camino: {len(camino) - 1} aristas.")
                # encontrar_camino_minimo_bfs ya imprime "No se encontró camino..." o errores de IDs.
                # else:
                #     print("No se encontró un camino entre los usuarios especificados o IDs inválidos.")
            print("--- Fin de Encontrar Camino Más Corto ---")
        elif opcion == '0':
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")