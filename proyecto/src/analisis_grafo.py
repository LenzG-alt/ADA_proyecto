# analisis_grafo.py
import networkx as nx
import logging
from utils import medir_tiempo
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np # Asegurarse de que numpy está importado si se usa directamente
from tqdm import tqdm

# --- Componentes Conexas ---
@medir_tiempo
def analizar_componentes_conexas(grafo_nx):
    """
    Encuentra y analiza las componentes conexas (fuertemente conexas para grafos dirigidos).
    """
    if not isinstance(grafo_nx, nx.DiGraph):
        logging.error("El análisis de componentes fuertemente conexas requiere un grafo NetworkX Dirigido.")
        return

    if grafo_nx.number_of_nodes() == 0:
        logging.info("El grafo está vacío. No hay componentes conexas para analizar.")
        return

    logging.info("Calculando componentes fuertemente conexas...")
    # Envolver el iterador de NetworkX con tqdm si es posible, o la operación completa.
    # nx.strongly_connected_components devuelve un generador. Convertirlo a lista puede ser la operación costosa.
    # Para mostrar progreso en la conversión a lista:
    componentes_generator = nx.strongly_connected_components(grafo_nx)
    # No es directo poner tqdm en la conversión de un generador desconocido sin saber su "longitud"
    # Lo más sencillo es que la barra de progreso general en main.py cubra esta llamada.
    # Si fuera un bucle explícito, sería:
    # componentes_fc = [comp for comp in tqdm(componentes_generator, desc="Procesando componentes")]
    componentes_fc = list(componentes_generator)


    if not componentes_fc:
        logging.info("No se encontraron componentes fuertemente conexas.")
        return

    num_componentes = len(componentes_fc)
    logging.info(f"Número de componentes fuertemente conexas: {num_componentes}")

    tamanos_componentes = [len(c) for c in componentes_fc]
    logging.info(f"Tamaño de la componente fuertemente conexa más grande: {max(tamanos_componentes) if tamanos_componentes else 0}")
    logging.info(f"Tamaño promedio de las componentes fuertemente conexas: {np.mean(tamanos_componentes):.2f}" if tamanos_componentes else "N/A")

    # Visualización de la distribución de tamaños de componentes (opcional, si hay muchas)
    if num_componentes > 1:
        plt.figure(figsize=(10, 6))
        sns.histplot(tamanos_componentes, bins=min(50, num_componentes), kde=False)
        plt.title('Distribución de Tamaños de Componentes Fuertemente Conexas')
        plt.xlabel('Tamaño de la Componente')
        plt.ylabel('Frecuencia')
        plt.yscale('log') # Escala logarítmica si hay mucha variación
        plt.xscale('log')
        os.makedirs("resultados/graficos/analisis", exist_ok=True)
        plt.savefig("resultados/graficos/analisis/distribucion_tamanos_componentes_fc.png")
        plt.close()
        logging.info("Gráfico de distribución de tamaños de componentes guardado.")

    return componentes_fc

# --- Métricas de Centralidad ---
@medir_tiempo
def calcular_metricas_centralidad(grafo_nx, top_n=10):
    """
    Calcula y muestra métricas de centralidad: grado, intermediación y cercanía.
    """
    if not grafo_nx.nodes():
        logging.info("Grafo vacío, no se pueden calcular métricas de centralidad.")
        return

    logging.info("Calculando centralidad de grado...")
    # Para DiGraph, degree() da grado total. in_degree() y out_degree() para específicos.
    centralidad_grado_salida = nx.out_degree_centrality(grafo_nx)
    centralidad_grado_entrada = nx.in_degree_centrality(grafo_nx)

    # logging.info(f"Top {top_n} nodos por centralidad de grado (salida): {sorted(centralidad_grado_salida.items(), key=lambda item: item[1], reverse=True)[:top_n]}")
    # logging.info(f"Top {top_n} nodos por centralidad de grado (entrada): {sorted(centralidad_grado_entrada.items(), key=lambda item: item[1], reverse=True)[:top_n]}")

    # PageRank (otra forma de centralidad de grado/influencia)
    logging.info("Calculando PageRank...")
    pagerank = {} # Definir por defecto
    try:
        # nx.pagerank es una operación única. La barra en main.py la cubrirá.
        pagerank_calc = nx.pagerank(grafo_nx, alpha=0.85)
        pagerank = dict(sorted(pagerank_calc.items(), key=lambda item: item[1], reverse=True)) # Guardar ordenado

        logging.info(f"Top {top_n} nodos por PageRank: {list(pagerank.items())[:top_n]}")

        os.makedirs("resultados/metricas", exist_ok=True)
        # tqdm para el bucle de escritura, aunque será rápido si pagerank ya está calculado.
        with open("resultados/metricas/pagerank.txt", "w") as f, \
             tqdm(total=len(pagerank), desc="Guardando PageRank") as pbar:
            for nodo, pr_valor in pagerank.items(): # Iterar sobre el dict ya ordenado
                f.write(f"{nodo}: {pr_valor:.6f}\n")
                pbar.update(1)
        logging.info("Valores de PageRank guardados en resultados/metricas/pagerank.txt")
    except Exception as e:
        logging.error(f"Error al calcular PageRank: {e}")
        pagerank = None # Indicar fallo


    # Centralidad de Intermediación (Betweenness Centrality) - Puede ser costosa
    # k = min(1000, grafo_nx.number_of_nodes() // 10) # Muestreo para grafos grandes
    # if k > 10: # Solo calcular si el muestreo es razonable
    #     logging.info(f"Calculando centralidad de intermediación (aproximada con k={k} muestras)...")
    #     try:
    #         centralidad_intermediacion = nx.betweenness_centrality(grafo_nx, k=k, normalized=True)
    #         logging.info(f"Top {top_n} nodos por centralidad de intermediación: {sorted(centralidad_intermediacion.items(), key=lambda item: item[1], reverse=True)[:top_n]}")
    #     except Exception as e:
    #         logging.error(f"Error al calcular centralidad de intermediación: {e}")
    # else:
    #     logging.info("Grafo demasiado pequeño o k demasiado bajo para muestreo de centralidad de intermediación, omitiendo.")


    # Centralidad de Cercanía (Closeness Centrality) - Costosa para grafos no fuertemente conexos
    # Considerar calcular solo para la componente gigante si aplica.
    # logging.info("Calculando centralidad de cercanía (puede ser lento)...")
    # try:
    #     # Para grafos desconectados, se calcula para cada componente o la más grande
    #     componentes_fc = list(nx.strongly_connected_components(grafo_nx))
    #     if componentes_fc:
    #         componente_gigante_nodos = max(componentes_fc, key=len)
    #         subgrafo_gigante = grafo_nx.subgraph(componente_gigante_nodos)
    #         if subgrafo_gigante.number_of_nodes() > 1: # Closeness centrality necesita al menos 2 nodos
    #             centralidad_cercania = nx.closeness_centrality(subgrafo_gigante)
    #             logging.info(f"Top {top_n} nodos por centralidad de cercanía (en la comp. gigante): {sorted(centralidad_cercania.items(), key=lambda item: item[1], reverse=True)[:top_n]}")
    #         else:
    #             logging.info("Componente gigante demasiado pequeña para centralidad de cercanía.")
    #     else:
    #         logging.info("No hay componentes fuertemente conexas para calcular centralidad de cercanía.")
    # except Exception as e:
    #     logging.error(f"Error al calcular centralidad de cercanía: {e}")

    return {
        "pagerank": pagerank if 'pagerank' in locals() else None,
        # "betweenness": centralidad_intermediacion if 'centralidad_intermediacion' in locals() else None,
        # "closeness": centralidad_cercania if 'centralidad_cercania' in locals() else None
    }

# --- Coeficiente de Clustering ---
@medir_tiempo
def calcular_coeficiente_clustering(grafo_nx):
    """
    Calcula el coeficiente de clustering promedio del grafo.
    """
    if not grafo_nx.nodes():
        logging.info("Grafo vacío, no se puede calcular coeficiente de clustering.")
        return None

    logging.info("Calculando coeficiente de clustering promedio...")
    # Para DiGraph, clustering se interpreta de varias maneras. NetworkX usa la definición para grafos no dirigidos
    # si se le pasa un DiGraph, por lo que es mejor convertirlo o usar una métrica específica para dirigidos si es necesario.
    # Por ahora, usaremos el promedio del clustering de la versión no dirigida como una aproximación general.

    try:
        # clustering_promedio = nx.average_clustering(grafo_nx) # Para DiGraph, esto puede dar resultados basados en el grafo no dirigido subyacente.
        # Para ser más precisos con grafos dirigidos, se podría considerar el clustering para cada nodo
        # y luego promediar, o usar métricas específicas de grafos dirigidos si el PDF lo detalla.
        # Si el PDF se refiere al clustering general, nx.average_clustering(G.to_undirected()) es más estándar.

        if grafo_nx.is_directed():
            # NetworkX calcula el clustering para DiGraphs considerando ciclos de longitud 3.
            # O se puede convertir a no dirigido para el clustering tradicional.
            # El PDF menciona "coeficiente de clustering", que usualmente se refiere al de grafos no dirigidos.
            # Vamos a usar la conversión a no dirigido para esta métrica general.
            clustering_promedio = nx.average_clustering(grafo_nx.to_undirected())
            logging.info(f"Coeficiente de clustering promedio (basado en la versión no dirigida): {clustering_promedio:.4f}")
        else:
            clustering_promedio = nx.average_clustering(grafo_nx)
            logging.info(f"Coeficiente de clustering promedio: {clustering_promedio:.4f}")

        # Distribución del coeficiente de clustering por nodo
        clustering_nodos = nx.clustering(grafo_nx.to_undirected()) # Usar no dirigido para la distribución también
        # logging.info(f"Coeficientes de clustering individuales (muestra): {list(clustering_nodos.items())[:5]}")

        plt.figure(figsize=(10, 6))
        sns.histplot(list(clustering_nodos.values()), bins=50, kde=False)
        plt.title('Distribución del Coeficiente de Clustering por Nodo')
        plt.xlabel('Coeficiente de Clustering')
        plt.ylabel('Frecuencia')
        os.makedirs("resultados/graficos/analisis", exist_ok=True)
        plt.savefig("resultados/graficos/analisis/distribucion_clustering.png")
        plt.close()
        logging.info("Gráfico de distribución de coeficientes de clustering guardado.")

        # Visualización (esto es rápido, no necesita tqdm aquí)
        plt.figure(figsize=(10, 6))
        sns.histplot(list(clustering_nodos.values()), bins=50, kde=False)
        plt.title('Distribución del Coeficiente de Clustering por Nodo')
        plt.xlabel('Coeficiente de Clustering')
        plt.ylabel('Frecuencia')
        os.makedirs("resultados/graficos/analisis", exist_ok=True)
        plt.savefig("resultados/graficos/analisis/distribucion_clustering.png")
        plt.close()
        logging.info("Gráfico de distribución de coeficientes de clustering guardado.")

    except Exception as e:
        logging.error(f"Error al calcular coeficiente de clustering: {e}")
        clustering_promedio = None

    return clustering_promedio


# --- Detección de Comunidades ---
@medir_tiempo
def encontrar_comunidades(grafo_nx, metodo='louvain'):
    """
    Encuentra comunidades en el grafo usando el algoritmo especificado.
    Louvain es una buena opción para grafos grandes y generalmente se aplica a no dirigidos.
    """
    if not grafo_nx.nodes():
        logging.info("Grafo vacío, no se pueden detectar comunidades.")
        return None

    logging.info(f"Detectando comunidades usando el método {metodo}...")

    # El algoritmo de Louvain espera un grafo no dirigido.
    # Si el grafo es dirigido, podemos convertirlo o usar algoritmos específicos para dirigidos si el PDF lo requiere.
    # Por ahora, asumimos que una visión general de comunidades en la estructura no dirigida es útil.
    grafo_para_comunidades = grafo_nx
    if grafo_nx.is_directed():
        logging.info("Convirtiendo grafo a no dirigido para detección de comunidades Louvain.")
        grafo_para_comunidades = grafo_nx.to_undirected() ##demora demasiado crear un grafo no dirigido

    if metodo == 'louvain':
        try:
            # Requiere python-louvain (community)
            import community as community_louvain
            partition = community_louvain.best_partition(grafo_para_comunidades)
            num_comunidades = len(set(partition.values()))
            logging.info(f"Número de comunidades detectadas (Louvain): {num_comunidades}")

            # Tamaños de las comunidades
            tamanos_comunidades = {}
            # Usar tqdm para iterar sobre la partición si es grande
            for node, comm_id in tqdm(partition.items(), desc="Calculando tamaños de comunidad", total=len(partition)):
                tamanos_comunidades[comm_id] = tamanos_comunidades.get(comm_id, 0) + 1

            logging.info(f"Tamaño de las comunidades más grandes (Louvain): {sorted(tamanos_comunidades.values(), reverse=True)[:min(5, num_comunidades)]}")

            # Guardar partición
            os.makedirs("resultados/metricas", exist_ok=True)
            with open("resultados/metricas/comunidades_louvain.txt", "w") as f, \
                 tqdm(total=len(partition), desc="Guardando partición Louvain") as pbar:
                for node, comm_id in partition.items():
                    f.write(f"{node}: {comm_id}\n")
                    pbar.update(1)
            logging.info("Partición de comunidades Louvain guardada.")
            return partition
        except ImportError:
            logging.error("Librería 'community' (python-louvain) no encontrada. No se pueden detectar comunidades con Louvain.")
            return None
        except Exception as e:
            logging.error(f"Error detectando comunidades con Louvain: {e}")
            return None
    else:
        logging.warning(f"Método de detección de comunidades '{metodo}' no implementado.")
        return None

# --- Caminos Más Cortos y Diámetro ---
@medir_tiempo
def calcular_caminos_cortos(grafo_nx, inicio=None, fin=None):
    """
    Calcula la longitud del camino más corto entre dos nodos o el diámetro/radio si no se especifican.
    """
    if not grafo_nx.nodes():
        logging.info("Grafo vacío, no se pueden calcular caminos.")
        return

    if inicio is not None and fin is not None:
        try:
            if nx.has_path(grafo_nx, source=inicio, target=fin):
                longitud = nx.shortest_path_length(grafo_nx, source=inicio, target=fin)
                # camino = nx.shortest_path(grafo_nx, source=inicio, target=fin) # El camino en sí
                logging.info(f"Longitud del camino más corto entre {inicio} y {fin}: {longitud}")
                return longitud
            else:
                logging.info(f"No hay camino entre {inicio} y {fin}.")
                return float('inf')
        except nx.NodeNotFound:
            logging.warning(f"Nodo {inicio} o {fin} no encontrado en el grafo.")
            return None
        except Exception as e:
            logging.error(f"Error calculando camino más corto: {e}")
            return None
    else:
        # Calcular diámetro y radio (costoso, especialmente para grafos grandes o desconectados)
        # Se recomienda hacerlo sobre la componente fuertemente conexa más grande.
        logging.info("Calculando diámetro y radio (puede ser muy lento)...")
        # Primero, verificar si el grafo es fuertemente conexo (para dirigidos)
        if grafo_nx.is_directed():
            if nx.is_strongly_connected(grafo_nx):
                try:
                    diametro = nx.diameter(grafo_nx)
                    logging.info(f"Diámetro del grafo (dirigido y fuertemente conexo): {diametro}")
                    # radio = nx.radius(grafo_nx) # Radius también es costoso
                    # logging.info(f"Radio del grafo: {radio}")
                except Exception as e:
                    logging.error(f"Error calculando diámetro/radio para grafo fuertemente conexo: {e}")
            else:
                logging.info("El grafo dirigido no es fuertemente conexo. El diámetro es infinito.")
                logging.info("Considerar calcular para la componente fuertemente conexa más grande:")
                componentes_fc = list(nx.strongly_connected_components(grafo_nx))
                if componentes_fc:
                    comp_gigante_nodos = max(componentes_fc, key=len)
                    subgrafo_gigante = grafo_nx.subgraph(comp_gigante_nodos)
                    if subgrafo_gigante.number_of_nodes() > 1:
                        try:
                            diametro_comp = nx.diameter(subgrafo_gigante)
                            logging.info(f"Diámetro de la componente fuertemente conexa más grande: {diametro_comp}")
                        except Exception as e:
                             logging.error(f"Error calculando diámetro de la comp. gigante: {e}")
                    else:
                        logging.info("Componente gigante muy pequeña para calcular diámetro.")
                else:
                    logging.info("No hay componentes fuertemente conexas.")
        else: # Grafo no dirigido
            if nx.is_connected(grafo_nx):
                try:
                    diametro = nx.diameter(grafo_nx)
                    logging.info(f"Diámetro del grafo (no dirigido y conexo): {diametro}")
                except Exception as e:
                    logging.error(f"Error calculando diámetro para grafo conexo: {e}")
            else:
                logging.info("El grafo no dirigido no es conexo. El diámetro es infinito.")
                # Similar lógica para componente gigante si se quisiera.

# --- Análisis de Mundo Pequeño ---
@medir_tiempo
def analizar_propiedades_mundo_pequeno(grafo_nx, niter=1, nrand=1):
    """
    Analiza si el grafo tiene propiedades de "mundo pequeño" (alto clustering y bajo camino promedio).
    Compara con grafos aleatorios equivalentes.
    Para grafos dirigidos, el concepto es más complejo. NetworkX ofrece `sigma` y `omega`
    para grafos no dirigidos.
    """
    if not grafo_nx.nodes() or grafo_nx.number_of_nodes() < 10: # Arbitrario, pero para grafos muy pequeños no tiene mucho sentido
        logging.info("Grafo demasiado pequeño o vacío para análisis de mundo pequeño significativo.")
        return

    logging.info("Analizando propiedades de 'Mundo Pequeño'...")

    # Se suele hacer en la componente gigante y para grafos no dirigidos.
    G_undirected = grafo_nx.to_undirected()

    # Tomar la componente conectada más grande
    componentes_conectadas = list(nx.connected_components(G_undirected))
    if not componentes_conectadas:
        logging.info("No hay componentes conectadas en la versión no dirigida.")
        return

    comp_gigante_nodos = max(componentes_conectadas, key=len)
    G_comp_gigante = G_undirected.subgraph(comp_gigante_nodos)

    if G_comp_gigante.number_of_nodes() < 10:
        logging.info("Componente gigante demasiado pequeña para análisis de mundo pequeño.")
        return

    try:
        # Coeficiente de clustering de la componente gigante
        C = nx.average_clustering(G_comp_gigante)
        logging.info(f"Coeficiente de clustering (comp. gigante no dirigida): {C:.4f}")

        # Longitud promedio del camino más corto de la componente gigante
        L = nx.average_shortest_path_length(G_comp_gigante)
        logging.info(f"Longitud promedio del camino más corto (comp. gigante no dirigida): {L:.4f}")

        # Para comparar, se pueden usar métricas de NetworkX si el grafo es no dirigido
        # sigma = nx.sigma(G_comp_gigante, niter=niter, nrand=nrand, seed=42)
        # omega = nx.omega(G_comp_gigante, niter=niter, nrand=nrand, seed=42)
        # logging.info(f"Sigma (Small-worldness): {sigma:.4f} (Valores > 1 indican mundo pequeño)")
        # logging.info(f"Omega (Small-worldness): {omega:.4f} (Valores cercanos a 0 indican mundo pequeño)")
        logging.info("Para una evaluación formal de mundo pequeño (sigma, omega), se necesitarían comparaciones con grafos aleatorios, lo cual puede ser costoso y está más allá de una implementación simple aquí.")
        logging.info("Un alto C y bajo L son indicativos de propiedades de mundo pequeño.")

    except Exception as e:
        logging.error(f"Error durante el análisis de mundo pequeño: {e}")

        