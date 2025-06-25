# main.py
import time
import os
from datetime import datetime # Added for timestamp logging

# Importar NUM_USERS de data_generator para saber con cuántos usuarios se generaron los datos
# si el usuario ejecuta data_generator.py standalone primero.
# Si main.py controla la generación, usará su propia constante.
from data_generator import generate_location_data, generate_user_data
# No necesitamos importar NUM_USERS de data_generator aquí si main controla la generación.
# from data_generator import NUM_USERS as DEFAULT_NUM_USERS_FROM_GENERATOR

from graph_utils import SocialGraph
from network_algorithms import (
    average_shortest_path_length,
    louvain_optimized, # Cambiado de simplified_louvain
    prim_mst
)
from visualizer import visualize_network_plotly, visualize_sample_graph_mpl

# Definir el número de usuarios para la simulación controlada por main.py
# Esto anula el NUM_USERS que podría estar en data_generator.py si se ejecutó standalone.
# Para pruebas en este entorno, mantenemos un número pequeño.
# Para tus pruebas locales con archivos grandes, este valor no se usa si use_simulated_data=False.
MAIN_SIMULATION_NUM_USERS = 100 # Usado solo si use_simulated_data=True

def run_analysis_pipeline(use_simulated_data=True, locations_file=None, users_file=None):
    """
    Ejecuta el pipeline completo de análisis de grafos, ahora usando funciones optimizadas.
    """
    start_datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"--- Pipeline de Análisis Iniciado: {start_datetime_str} ---")
    pipeline_start_time = time.time()

    actual_loc_file = locations_file
    actual_user_file = users_file

    if use_simulated_data:
        print(f"Generando datos simulados para {MAIN_SIMULATION_NUM_USERS} usuarios...")
        sim_loc_file = "simulated_locations.txt"
        sim_user_file = "simulated_users.txt"
        # Pasar explícitamente el número de usuarios a generar
        generate_location_data(sim_loc_file, num_users_to_generate=MAIN_SIMULATION_NUM_USERS)
        generate_user_data(sim_user_file, num_users_to_generate=MAIN_SIMULATION_NUM_USERS)
        actual_loc_file = sim_loc_file
        actual_user_file = sim_user_file
        print(f"Datos simulados generados ({sim_loc_file}, {sim_user_file}).\n")
    elif not actual_loc_file or not actual_user_file:
        print("Error: Se deben proporcionar archivos de ubicaciones y usuarios si no se usan datos simulados.")
        return
    elif not os.path.exists(actual_loc_file) or not os.path.exists(actual_user_file):
        print(f"Error: Archivos de datos no encontrados: {actual_loc_file}, {actual_user_file}")
        return

    # 1. Cargar Grafo usando métodos optimizados
    print("--- 1. Cargando Grafo (Optimizado) ---")
    graph = SocialGraph()

    # Determinar batch_size basado en el tamaño de la simulación o un valor por defecto grande
    # si se usan archivos externos (donde no conocemos el tamaño de antemano).
    if use_simulated_data:
        loc_batch_size = max(10, MAIN_SIMULATION_NUM_USERS // 20) # Al menos 10, o 5%
        conn_batch_size_report = max(10, MAIN_SIMULATION_NUM_USERS // 20)
    else: # Para archivos externos grandes, usar un batch size mayor por defecto
        loc_batch_size = 100000
        conn_batch_size_report = 100000

    graph.load_locations_batched(actual_loc_file, batch_size=loc_batch_size)
    graph.load_users_connections_batched(actual_user_file, batch_size_progress_report=conn_batch_size_report)

    if graph.get_number_of_nodes(force_recount=False) == 0:
        print("Grafo vacío después de la carga. Finalizando análisis.")
        return

    # Opcional: Precomputar in-degrees. Louvain_optimized actual no lo usa, pero otros análisis podrían.
    # print("\nPre-calculando grados de entrada (opcional)...")
    # graph.precompute_in_degrees()

    graph.print_graph_summary()


    # 2. Análisis Avanzado
    print("\n--- 2. Análisis Avanzado (con Algoritmos Optimizados) ---")

    print("\nCalculando longitud promedio del camino más corto...")
    num_nodes_for_asp = graph.get_number_of_nodes()
    sample_size_asp = 100 if num_nodes_for_asp > 1000 else None
    if num_nodes_for_asp <= 200 : sample_size_asp = None # Para simulaciones pequeñas, calcular todos.

    avg_path_len = average_shortest_path_length(graph, sample_size=sample_size_asp)
    print(f"Longitud promedio del camino más corto (sample_size={sample_size_asp if sample_size_asp is not None else 'all'}): {avg_path_len:.2f}")


    print("\nDetectando comunidades (Louvain optimizado)...")
    communities = louvain_optimized(graph, max_passes=5)
    if communities:
        num_detected_communities = len(set(communities.values()))
        print(f"Número de comunidades detectadas: {num_detected_communities}")
    else:
        print("No se detectaron comunidades.")

    print("\nCalculando Árbol de Expansión Mínima (Prim)...")
    mst = prim_mst(graph)
    if mst:
        print(f"MST encontrado con {len(mst)} aristas.")
    else:
        print("No se pudo generar el MST.")


    # 3. Visualización
    print("\n--- 3. Visualización Interactiva (Plotly) ---")
    # La lógica de muestreo para grafos grandes ahora está dentro de visualize_network_plotly.
    # Ya no es necesario el chequeo de tamaño aquí para omitir la visualización.
    print("Generando visualización de la red (Plotly)...")
    layout_type_vis = 'locations' if graph.locations and len(graph.locations) > 0 else 'random'

    # visualize_network_plotly ahora maneja internamente el muestreo si el grafo es grande.
    fig = visualize_network_plotly(graph, communities=communities, layout_type=layout_type_vis)

    if fig and (fig.data or fig.layout.annotations): # Chequeo básico si la figura tiene contenido
        output_html_file = "network_visualization.html"
        try:
            fig.write_html(output_html_file)
            print(f"Visualización guardada en: {os.path.abspath(output_html_file)}")
            print(f"AIDERAIDER_CONTENT_DISPLAY_HTML:{os.path.abspath(output_html_file)}")
        except Exception as e:
            print(f"Error al guardar la visualización HTML: {e}")
    else:
        print("No se generó la figura de Plotly o estaba vacía (posiblemente debido a un grafo vacío o error en la visualización).")

    pipeline_end_time = time.time()
    total_duration_seconds = pipeline_end_time - pipeline_start_time
    end_datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n--- Pipeline de Análisis Finalizado: {end_datetime_str} ---")
    print(f"Duración total del análisis: {total_duration_seconds:.2f} segundos.")

    # Devolver el grafo para el menú interactivo
    return graph

def interactive_menu(graph):
    """
    Muestra un menú interactivo para realizar análisis adicionales en el grafo.
    """
    if not graph or graph.get_number_of_nodes(force_recount=False) == 0:
        print("\nNo hay datos de grafo cargados o el grafo está vacío. El menú interactivo no puede continuar.")
        return

    print("\n--- Menú Interactivo ---")
    while True:
        print("\nOpciones:")
        print("1. Mostrar Top N usuarios influyentes (por in-degree)")
        print("2. Visualizar muestra del grafo (Matplotlib)")
        print("3. Salir del menú")

        choice = input("Selecciona una opción (1-3): ")

        if choice == '1':
            try:
                n_str = input("Introduce el número de usuarios top a mostrar (ej. 10): ")
                n_top = int(n_str)
                if n_top <= 0:
                    print("Por favor, introduce un número positivo.")
                    continue

                print(f"\n--- Top {n_top} Usuarios Más Influyentes (por In-Degree) ---")
                # La función get_top_n_influencers está en SocialGraph
                top_influencers = graph.get_top_n_influencers(n=n_top)

                if not top_influencers:
                    print("No se encontraron influencers o el grafo no tiene suficientes datos.")
                else:
                    for i, (user_id, in_degree) in enumerate(top_influencers):
                        print(f"{i+1}. Usuario ID: {user_id}, In-Degree (Seguidores): {in_degree}")
            except ValueError:
                print("Entrada no válida. Por favor, introduce un número.")
            except Exception as e:
                print(f"Ocurrió un error al obtener los top influencers: {e}")

        elif choice == '2':
            try:
                sample_size_str = input("Introduce el tamaño de la muestra para visualización (ej. 50, default 50): ")
                if not sample_size_str.strip(): # Si está vacío, usar default
                    sample_size_val = 50
                else:
                    sample_size_val = int(sample_size_str)

                if sample_size_val <= 0:
                    print("Por favor, introduce un número positivo para el tamaño de la muestra.")
                    continue

                visualize_sample_graph_mpl(graph, sample_size=sample_size_val)
            except ValueError:
                print("Entrada no válida. Por favor, introduce un número para el tamaño de la muestra.")
            except Exception as e:
                print(f"Ocurrió un error durante la visualización de la muestra: {e}")
        elif choice == '3':
            print("Saliendo del menú interactivo.")
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")


if __name__ == "__main__":
    # ... (resto del código __main__ sin cambios hasta la llamada a run_analysis_pipeline)
    try:
        import plotly
    except ImportError:
        print("Error: Plotly no está instalado. Ejecuta 'pip install plotly'. La visualización no funcionará.")

    # print(f"Ejecutando pipeline con datos simulados (MAIN_SIMULATION_NUM_USERS={MAIN_SIMULATION_NUM_USERS})...")
    # graph_data = run_analysis_pipeline(use_simulated_data=True)

    # Para probar con archivos externos que TÚ proporciones:
    print("\n--- Ejecución con Archivos Externos ---")
    print("Por favor, asegúrate de que los siguientes archivos existen y contienen los datos esperados.")
    external_locations = "datos/10_million_location.txt" # Reemplaza con tu nombre de archivo
    external_users = "datos/10_million_user.txt"       # Reemplaza con tu nombre de archivo
    print(f"Intentando cargar desde: {external_locations} y {external_users}")

    graph_data = run_analysis_pipeline(use_simulated_data=False,
                                       locations_file=external_locations,
                                       users_file=external_users)

    # Iniciar menú interactivo si el grafo se cargó
    if graph_data:
        interactive_menu(graph_data)
    else:
        print("No se pudo cargar el grafo, omitiendo menú interactivo.")
