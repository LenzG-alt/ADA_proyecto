# visualizer.py
import plotly.graph_objects as go
import random
import matplotlib
matplotlib.use('Agg') # Use Agg backend for non-interactive environments if needed.
import matplotlib.pyplot as plt
import networkx as nx

# Umbral y tamaño de muestra para la visualización de Plotly en grafos grandes
PLOTLY_VISUALIZATION_THRESHOLD = 2500
PLOTLY_SAMPLE_SIZE_LARGE_GRAPH = 500

def visualize_network_plotly(graph, communities=None, layout_type='random'):
    """
    Crea una visualización interactiva del grafo de red usando Plotly.
    Para grafos grandes (más de PLOTLY_VISUALIZATION_THRESHOLD nodos), visualiza una muestra.
    Los nodos se posicionan usando sus ubicaciones si están disponibles para la muestra,
    o un layout aleatorio en caso contrario.

    Args:
        graph (SocialGraph): El objeto grafo.
        communities (dict, optional): Un diccionario {node_id: community_id} para colorear nodos.
        layout_type (str): 'locations', 'random'.
                           Si es 'locations' y no hay ubicaciones, recurre a 'random'.

    Returns:
        plotly.graph_objects.Figure: La figura de Plotly.
    """
    original_node_count = graph.get_number_of_nodes()
    is_sampled_visualization = False

    if original_node_count == 0:
        print("No nodes to visualize.")
        return go.Figure()

    if original_node_count > PLOTLY_VISUALIZATION_THRESHOLD:
        is_sampled_visualization = True
        print(f"Graph with {original_node_count} nodes exceeds threshold ({PLOTLY_VISUALIZATION_THRESHOLD}). Visualizing a sample of {PLOTLY_SAMPLE_SIZE_LARGE_GRAPH} nodes.")
        all_graph_nodes = graph.get_nodes()
        if PLOTLY_SAMPLE_SIZE_LARGE_GRAPH >= original_node_count:
            nodes_to_process = all_graph_nodes # Muestra es mayor o igual que el grafo
        else:
            nodes_to_process = random.sample(all_graph_nodes, PLOTLY_SAMPLE_SIZE_LARGE_GRAPH)
    else:
        nodes_to_process = graph.get_nodes()

    if not nodes_to_process: # Si después del muestreo (o no) no hay nodos
        print("No nodes selected for visualization after potential sampling.")
        return go.Figure()

    # --- Preparar datos de Nodos (basado en nodes_to_process) ---
    node_x = []
    node_y = []
    node_ids_to_draw = []
    node_colors_values = []
    node_hover_texts = []

    # Determinar si usar ubicaciones reales o generar aleatorias
    can_use_locations = layout_type == 'locations' and graph.locations and len(graph.locations) > 0

    if can_use_locations:
        print("Layout: Using provided node locations for (sampled) nodes.")
        # Iterar sobre los nodos seleccionados para el proceso (pueden ser una muestra)
        for node_id in nodes_to_process:
            if node_id in graph.locations:
                lat, lon = graph.locations[node_id]
                node_x.append(lon) # Longitud para X
                node_y.append(lat) # Latitud para Y
                node_ids_to_draw.append(node_id)

        if not node_ids_to_draw: # Si 'locations' fue elegido pero ningún nodo (de la muestra) tenía ubicación
            print("Warning: 'locations' layout chosen, but no (sampled) nodes had location data. Falling back to random.")
            can_use_locations = False

    if not can_use_locations: # Random layout for (sampled) nodes
        print("Layout: Using random positions for (sampled) nodes.")
        node_ids_to_draw = list(nodes_to_process) # Usar los nodos seleccionados (muestra o todos)
        node_x = [random.uniform(0, 100) for _ in range(len(node_ids_to_draw))]
        node_y = [random.uniform(0, 100) for _ in range(len(node_ids_to_draw))]

    if not node_ids_to_draw: # Si después de todo, no hay nodos para dibujar
        print("No nodes have coordinates for visualization (after sampling and layout attempt).")
        return go.Figure()

    # Mapear node_ids (los que se van a dibujar, que son de la muestra si aplica) a sus índices
    node_map_idx = {node_id: i for i, node_id in enumerate(node_ids_to_draw)}

    # Colores de comunidad y textos hover (para los nodos que se van a dibujar)
    if communities:
        unique_comm_ids = sorted(list(set(c_id for c_id in communities.values() if c_id is not None)))
        num_unique_communities = len(unique_comm_ids)

        # Paleta de colores simple (Plotly ciclará si hay más comunidades que colores)
        color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                         '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

        # Mapeo estable de ID de comunidad a un color de la paleta
        comm_id_to_color = {comm_id: color_palette[i % len(color_palette)] for i, comm_id in enumerate(unique_comm_ids)}

        for node_id in node_ids_to_draw:
            comm_id = communities.get(node_id)
            node_colors_values.append(comm_id_to_color.get(comm_id, 'black')) # Negro para nodos sin comunidad asignada
            node_hover_texts.append(f"User: {node_id}<br>Community: {comm_id if comm_id is not None else 'N/A'}")
    else:
        node_colors_values = 'blue' # Color único si no hay comunidades
        for node_id in node_ids_to_draw:
            node_hover_texts.append(f"User: {node_id}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_hover_texts,
        marker=dict(
            showscale=False,
            color=node_colors_values,
            size=10,
            line_width=1,
            line_color='black'
        )
    )

    # --- Preparar datos de Aristas (solo entre nodos en node_ids_to_draw) ---
    edge_x = []
    edge_y = []
    num_edges_visualized = 0

    # Ajustar max_edges_to_draw si es una muestra.
    # Para una muestra de N nodos, un límite razonable podría ser N*k (e.g., N*5 o N*logN)
    # O simplemente un máximo absoluto más pequeño que para el grafo completo.
    if is_sampled_visualization:
        # Para una muestra de PLOTLY_SAMPLE_SIZE_LARGE_GRAPH nodos, un límite como N*5 o N*10
        max_edges_to_draw = PLOTLY_SAMPLE_SIZE_LARGE_GRAPH * 10
    else:
        # Para grafos pequeños, podemos permitir más aristas relativas al tamaño total,
        # pero aún así es bueno tener un cap.
        # graph.get_number_of_edges() es el número de aristas dirigidas.
        # Plotly dibuja una línea por arista.
        max_edges_to_draw = min(graph.get_number_of_edges(), 10000) # Cap a 10k aristas para Plotly

    # Iterar sobre los nodos que se van a dibujar (node_ids_to_draw)
    for u_id in node_ids_to_draw: # Estos son los nodos de la muestra (si aplica)
        u_idx = node_map_idx[u_id]

        for v_id in graph.adj.get(u_id, []):
            # Solo dibujar arista si el nodo destino (v_id) también está en la muestra (node_ids_to_draw)
            if v_id in node_map_idx:
                v_idx = node_map_idx[v_id]
                if num_edges_visualized < max_edges_to_draw:
                    edge_x.extend([node_x[u_idx], node_x[v_idx], None]) # None para romper la línea
                    edge_y.extend([node_y[u_idx], node_y[v_idx], None])
                    num_edges_visualized += 1
                else:
                    break
        if num_edges_visualized >= max_edges_to_draw:
            print(f"Warning: Reached maximum number of edges to draw for Plotly ({max_edges_to_draw}). Not all edges in the (sample) graph might be shown.")
            break

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.7, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # --- Crear Figura ---
    base_fig_title = "Visualización de Red Social"
    if is_sampled_visualization:
        base_fig_title += f" (Muestra de ~{len(node_ids_to_draw)} nodos de {original_node_count} totales)"

    fig_title = base_fig_title
    if communities:
        fig_title += " con Comunidades"
    if can_use_locations: # Este flag ahora indica si se usaron ubicaciones para los nodos (de la muestra)
        fig_title += " (Layout por Ubicaciones)"
    else:
        fig_title += " (Layout Aleatorio)"


    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=dict(text=fig_title, font=dict(size=16)),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=True),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, fixedrange=True),
                        plot_bgcolor='white' # Fondo blanco
                        )
                    )

    if can_use_locations:
        fig.update_layout(
            yaxis_scaleanchor="x", # Mantiene la proporción de aspecto si son coordenadas geo
            yaxis_scaleratio=1,
        )

    return fig

if __name__ == '__main__':
    print("Visualizer.py: Contiene la función visualize_network_plotly.")
    print("Ejecutar main.py para ver una demostración de visualización.")
    # Para una prueba rápida de que plotly está instalado y funciona:
    # try:
    #    fig = go.Figure(data=[go.Scatter(x=[1,2,3], y=[2,1,2])])
    #    print("Plotly figura simple creada. Para verla, necesitarías fig.show() o guardarla.")
    #    # fig.write_html("test_plotly.html")
    # except Exception as e:
    #    print(f"Error al crear figura Plotly: {e}")


def visualize_sample_graph_mpl(graph, sample_size=50):
    """
    Visualiza una muestra del grafo usando Matplotlib y NetworkX.
    Muestra una imagen estática.
    """
    if not graph or graph.get_number_of_nodes(force_recount=False) == 0:
        print("Grafo vacío o no cargado. No se puede visualizar la muestra.")
        return

    all_nodes = graph.get_nodes()
    if not all_nodes:
        print("No hay nodos en el grafo para muestrear.")
        return

    actual_sample_size = min(sample_size, len(all_nodes))
    if actual_sample_size == 0:
        print("Tamaño de muestra es 0. No se visualiza nada.")
        return

    print(f"\nGenerando visualización de muestra con Matplotlib/NetworkX para {actual_sample_size} nodos...")

    # Tomar una muestra de nodos
    sampled_nodes = random.sample(all_nodes, actual_sample_size)

    # Crear un subgrafo en NetworkX
    nx_graph = nx.Graph() # Usar grafo no dirigido para visualización simple

    # Añadir nodos muestreados
    for node_id in sampled_nodes:
        nx_graph.add_node(node_id)

    # Añadir aristas entre nodos muestreados
    # Esto puede ser lento si el grafo original es muy grande y self.adj es grande
    # Optimizacion: iterar solo sobre sampled_nodes en el bucle exterior
    edges_added_count = 0
    max_edges_to_draw_sample = actual_sample_size * 5 # Limitar aristas para claridad

    for u_id in sampled_nodes:
        if u_id in graph.adj: # Si el nodo u_id tiene conexiones salientes
            for v_id in graph.adj[u_id]:
                if v_id in nx_graph: # Si v_id también está en la muestra
                    if not nx_graph.has_edge(u_id, v_id): # Evitar duplicados para nx.Graph
                        nx_graph.add_edge(u_id, v_id)
                        edges_added_count +=1
                        if edges_added_count >= max_edges_to_draw_sample:
                            break
            if edges_added_count >= max_edges_to_draw_sample:
                print(f"Límite de {max_edges_to_draw_sample} aristas para la muestra alcanzado.")
                break

    if nx_graph.number_of_nodes() == 0:
        print("La muestra del grafo no contiene nodos después del procesamiento. No se puede visualizar.")
        return

    plt.figure(figsize=(10, 8))
    try:
        # Intentar un layout que tienda a separar componentes si el grafo es desconectado
        if nx.is_connected(nx_graph):
            pos = nx.spring_layout(nx_graph, k=0.15, iterations=20)
        else:
            # kamada_kawai puede ser lento para grafos grandes o desconectados.
            # spring_layout es un buen fallback.
            print("La muestra del grafo no es conexa, usando spring_layout.")
            pos = nx.spring_layout(nx_graph, k=0.15, iterations=20)

    except Exception as e_layout:
        print(f"Error durante el cálculo del layout ({e_layout}), usando random_layout como fallback.")
        pos = nx.random_layout(nx_graph)

    nx.draw(nx_graph, pos, with_labels=True, node_size=50, font_size=8, node_color='lightblue', edge_color='gray', width=0.5)
    plt.title(f"Muestra del Grafo de Red ({actual_sample_size} nodos, {nx_graph.number_of_edges()} aristas)")

    # Guardar en un archivo temporal y mostrar
    temp_image_file = "temp_graph_sample.png"
    try:
        plt.savefig(temp_image_file)
        plt.close() # Cerrar la figura para liberar memoria
        print(f"Visualización de muestra guardada como: {os.path.abspath(temp_image_file)}")
        # Mostrar la imagen al usuario (si el entorno Aider lo soporta)
        print(f"AIDERAIDER_CONTENT_DISPLAY_IMAGE:{os.path.abspath(temp_image_file)}")
    except Exception as e:
        print(f"Error al guardar o mostrar la imagen de muestra del grafo: {e}")
        plt.close() # Asegurar que se cierre la figura
