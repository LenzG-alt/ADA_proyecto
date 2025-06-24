# Proyecto: Análisis y Visualización del Grafo de la Red Social "X"

Este proyecto realiza un análisis exhaustivo de un grafo social generado a partir de datos de usuarios y sus conexiones en una red social hipotética denominada "X". Incluye la carga y preprocesamiento de datos, construcción del grafo, análisis exploratorio de datos (EDA), cálculo de métricas de red, detección de comunidades y visualización de resultados.

## Estructura del Proyecto

El proyecto está organizado en los siguientes directorios y archivos principales:

```
proyecto/
├── datos/
│   ├── 10_million_user.txt       # Dataset de conexiones de usuarios (ejemplo)
│   └── 10_million_location.txt   # Dataset de ubicaciones de usuarios (ejemplo)
├── resultados/
│   ├── graficos/                 # Gráficos generados por el análisis
│   │   ├── eda/
│   │   ├── analisis/
│   │   ├── visualizaciones_red/
│   │   └── geograficos/
│   ├── metricas/                 # Métricas calculadas (e.g., PageRank, comunidades)
│   └── registro_analisis.log     # Log detallado de la ejecución del análisis
├── src/
│   ├── main.py                   # Script principal para ejecutar el análisis completo
│   ├── config.py                 # Configuración de rutas y parámetros
│   ├── carga_datos.py            # Funciones para cargar los datasets
│   ├── construccion_grafo.py     # Funciones para construir el grafo con NetworkX
│   ├── eda.py                    # Funciones para el Análisis Exploratorio de Datos
│   ├── analisis_grafo.py         # Funciones para el análisis avanzado del grafo (métricas, comunidades, etc.)
│   ├── visualizacion.py          # Funciones para generar visualizaciones de la red
│   ├── geografia.py              # Funciones para el análisis y visualización de datos geográficos
│   └── utils.py                  # Utilidades (logger, medidor de tiempo, validadores)
└── README.md                     # Este archivo
```

## Requisitos

Las siguientes bibliotecas de Python son necesarias para ejecutar el proyecto:
*   pandas
*   numpy
*   matplotlib
*   seaborn
*   networkx
*   python-louvain (para detección de comunidades con el método Louvain)
*   scipy (dependencia de NetworkX para algunas funcionalidades como PageRank)

Puedes instalarlas usando pip:
```bash
pip install pandas numpy matplotlib seaborn networkx python-louvain scipy
```

## Ejecución

1.  **Preparar los Datos**:
    *   Coloca los archivos de datos `10_million_user.txt` y `10_million_location.txt` en la carpeta `proyecto/datos/`.
    *   Asegúrate de que los archivos tengan el formato esperado:
        *   `10_million_user.txt`: Cada línea representa un usuario. La línea contiene una lista de IDs de usuarios (enteros) a los que sigue el usuario actual, separados por comas. El ID del usuario actual se infiere por el número de línea (comenzando en 0).
        *   `10_million_location.txt`: Cada línea contiene la latitud y longitud de un usuario, separadas por una coma.

2.  **Configurar Parámetros (Opcional)**:
    *   Puedes ajustar el parámetro `MAX_USERS_TO_LOAD` en `proyecto/src/config.py` para limitar el número de usuarios a cargar y analizar. Esto es útil para pruebas rápidas con subconjuntos del dataset. Por defecto, está configurado para 100,000 usuarios.

3.  **Ejecutar el Análisis**:
    *   Navega al directorio raíz del proyecto (`proyecto/`).
    *   Ejecuta el script principal desde la raíz del proyecto o directamente:
        ```bash
        python src/main.py
        ```
    *   O si estás dentro de `proyecto/src/`:
        ```bash
        python main.py
        ```

4.  **Ver Resultados**:
    *   Los logs de la ejecución se guardarán en `proyecto/resultados/registro_analisis.log`.
    *   Los gráficos generados se encontrarán en las subcarpetas de `proyecto/resultados/graficos/`.
    *   Las métricas calculadas (como PageRank y particiones de comunidades) se guardarán en `proyecto/resultados/metricas/`.

## Funcionalidades Implementadas

*   **Carga de Datos**: Carga eficiente de datos de usuarios y ubicaciones, con manejo de errores y validación.
*   **Construcción de Grafo**: Creación de un grafo dirigido utilizando la biblioteca NetworkX.
*   **Análisis Exploratorio de Datos (EDA)**:
    *   Estadísticas básicas del grafo (número de nodos, aristas, densidad).
    *   Cálculo y visualización de la distribución de grados (entrada y salida).
    *   Detección de outliers en los grados.
    *   Análisis de correlación entre grados de entrada y salida.
*   **Análisis Avanzado del Grafo**:
    *   Detección y análisis de componentes fuertemente conexas.
    *   Cálculo de métricas de centralidad (PageRank; estructuras para intermediación y cercanía están presentes).
    *   Cálculo del coeficiente de clustering promedio y su distribución.
    *   Detección de comunidades (usando el algoritmo de Louvain).
    *   Cálculo de caminos más cortos y diámetro (sobre la componente gigante).
    *   Análisis de propiedades de "Mundo Pequeño" (coeficiente de clustering y longitud promedio de caminos).
*   **Visualizaciones**:
    *   Visualización de un subgrafo de la red.
    *   Gráficos de distribuciones (grados, PageRank, clustering, tamaño de componentes).
    *   Visualización de la distribución geográfica de los usuarios.
    *   Visualización de comunidades en el subgrafo.
*   **Logging y Medición de Tiempo**: Registro detallado de la ejecución y tiempos de las operaciones principales.

## Consideraciones

*   Algunos análisis avanzados (como centralidad de intermediación, cercanía completa, diámetro completo en grafos grandes y detección de comunidades con ciertos métodos) pueden ser computacionalmente intensivos. El script está configurado para ejecutar análisis que son factibles en tiempos razonables para el `MAX_USERS_TO_LOAD` por defecto. Para análisis más profundos con el dataset completo, se requerirá más tiempo y posiblemente más recursos computacionales.
*   Las rutas a los archivos de datos se configuran en `proyecto/src/config.py`. Asegúrate de que coincidan con la ubicación de tus archivos.
```
