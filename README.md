# INTEGRANTES
- Davis Arapa Chua
- Leonardo Pachari Gomez

# Analizador y Visualizador de Redes Sociales

Este proyecto proporciona un conjunto de herramientas para analizar y visualizar redes sociales. Permite generar datos simulados, cargar redes desde archivos, realizar diversos análisis algorítmicos (como detección de comunidades y cálculo de caminos más cortos) y visualizar la red de forma interactiva y estática.

## Características Principales

*   **Carga de Datos Eficiente**: Capacidad para cargar datos de redes sociales (ubicaciones y conexiones) desde archivos de texto, utilizando carga en lotes para manejar conjuntos de datos grandes.
*   **Representación de Grafo Social**: Modela la red mediante una clase `SocialGraph` que almacena nodos (usuarios), aristas (conexiones) y opcionalmente ubicaciones geográficas.
*   **Análisis de Red Avanzado**:
    *   **Longitud Promedio de Caminos Más Cortos**: Calcula esta métrica clave de la red.
    *   **Detección de Comunidades**: Implementa el algoritmo de Louvain (optimizado) para descubrir agrupaciones de usuarios.
    *   **Árbol de Expansión Mínima (MST)**: Genera el MST de la red usando el algoritmo de Prim.
    *   **Identificación de Influencers**: Lista los usuarios más influyentes según su número de conexiones entrantes (in-degree).
*   **Visualización de Redes**:
    *   **Interactiva (Plotly)**: Genera un archivo HTML (`network_visualization.html`) con un grafo interactivo. Soporta muestreo para redes grandes y coloreado de nodos por comunidad. Puede usar ubicaciones geográficas o un layout aleatorio.
    *   **Estática (Matplotlib/NetworkX)**: Permite visualizar una muestra del grafo como una imagen estática (`temp_graph_sample.png`).
*   **Pipeline Orquestado**: El script `main.py` gestiona el flujo completo desde la carga/generación de datos hasta el análisis y la visualización.
*   **Menú Interactivo en Consola**: Tras el análisis inicial, ofrece opciones para realizar exploraciones adicionales sobre el grafo cargado.
*   **Modularidad**: Código organizado en módulos Python con responsabilidades bien definidas.

## Requisitos

*   Python 3.x
*   Las siguientes librerías de Python (pueden instalarse mediante `pip`):
    *   `plotly`
    *   `matplotlib`
    *   `networkx`
    *   `tqdm`

    Ejemplo de instalación:
    ```bash
    pip install plotly matplotlib networkx tqdm
    ```

## Estructura del Proyecto

*   `main.py`: Punto de entrada principal. Orquesta la carga de datos, análisis y visualización. Contiene el menú interactivo.
*   `graph_utils.py`: Define la clase `SocialGraph` para la representación y manejo del grafo.
*   `network_algorithms.py`: Implementa los algoritmos de análisis de red (BFS, Louvain, Prim, etc.).
*   `visualizer.py`: Contiene las funciones para generar las visualizaciones interactivas (Plotly) y estáticas (Matplotlib).
*   `network_visualization.html`: (Archivo generado) Visualización interactiva de la red.
*   `temp_graph_sample.png`: (Archivo generado) Imagen de muestra de la red.
*   `datos/`: (Directorio opcional) Destinado a almacenar archivos de datos de entrada externos.

## Cómo Usar

1.  **Clonar el Repositorio (si aplica)**
    ```bash
    # git clone <repository_url>
    # cd <repository_directory>
    ```

2.  **Instalar Dependencias**
    ```bash
    pip install plotly matplotlib networkx tqdm
    ```

3.  **Preparar Datos**
    *   Cree un directorio llamado `datos` en la raíz del proyecto.
    *   Coloque sus archivos de datos allí. `main.py` por defecto busca:
        *   `datos/10_million_location.txt`: Formato `latitud,longitud` por línea.
        *   `datos/10_million_user.txt`: Formato `id_conectado1,id_conectado2,...` por línea.
    *   Puede modificar las rutas de los archivos directamente en `main.py` si es necesario.

4.  **Ejecutar el Pipeline Principal**
    ```bash
    python main.py
    ```
    *   Por defecto, `main.py` intentará cargar datos desde los archivos especificados en `external_locations` y `external_users` (e.g., `datos/10_million_location.txt`).
    *   Si desea **forzar el uso de datos simulados** generados por `main.py`:
        *   Edite `main.py`.
        *   En el bloque `if __name__ == "__main__":`, comente la llamada a `run_analysis_pipeline` que usa `use_simulated_data=False`.
        *   Descomente la línea: `graph_data = run_analysis_pipeline(use_simulated_data=True)`
    *   La ejecución mostrará progreso en la consola, resultados de los análisis, y generará `network_visualization.html`.
    *   Al finalizar el pipeline, se presentará un **menú interactivo** en la consola.

5.  **Menú Interactivo**
    Tras la ejecución del pipeline, el menú permite:
    *   **1. Mostrar Top N usuarios influyentes**: Pide un número N y lista los usuarios.
    *   **2. Visualizar muestra del grafo (Matplotlib)**: Pide un tamaño de muestra y genera `temp_graph_sample.png`.
    *   **3. Salir**.

## Archivos Generados

*   `network_visualization.html`: Visualización interactiva principal (Plotly).
*   `temp_graph_sample.png`: Imagen estática de una muestra del grafo (Matplotlib), generada desde el menú interactivo.


```
