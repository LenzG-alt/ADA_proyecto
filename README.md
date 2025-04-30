# Autor
Desarrollado como proyecto final del curso Algoritmos y Análisis de Datos (ADA).

## INTEGRANTEs
- `Davis Yovanny Arapa Chua`
- `Leonardo Rhapael Pachari GOomez`

# 🔍 Análisis de Redes Sociales a Gran Escala

Este proyecto tiene como objetivo realizar un análisis exploratorio de datos (EDA) y estructural sobre una red social simulada de hasta **10 millones de usuarios**, utilizando técnicas de análisis de grafos y geolocalización. Está diseñado para ser eficiente en memoria y escalable a grandes volúmenes de datos.

---
## Estructura del Proyecto
```bash
├── final_project_ada.py           # Script principal con todas las funcionalidades
├── 10_million_location.txt       # Archivo con coordenadas geográficas
├── 10_million_user.txt           # Archivo con las conexiones por usuario
├── datos_procesados/             # Salida de datos procesados (opcional)
└── README.md                     # Este documento
```

## 🧩 Descripción General

Este programa analiza una red social simulada con hasta 10 millones de usuarios y sus conexiones (seguidores/seguidos), junto con sus ubicaciones geográficas. Permite:

- Cargar datos masivos de forma optimizada.
- Construir un grafo dirigido con `NetworkX`.
- Calcular métricas estructurales de red (grado, centralidades).
- Buscar usuarios influyentes.
- Buscar usuarios cercanos a una ubicación geográfica.
- Guardar datos procesados para futuros análisis.
---

## ⚙️ Requisitos

Este proyecto está desarrollado en Python y requiere los siguientes paquetes:

```bash
pip install pandas numpy networkx tqdm psutil
```

## 📂 Archivos Esperados
Coloca los siguientes archivos en el mismo directorio del script:

- `10_million_location.txt` : coordenadas latitud,longitud por línea (sin encabezado).

- `10_million_user.txt` : lista de usuarios seguidos por cada usuario (una línea por usuario, separados por comas).

## ▶️  Como Ejecutar
Esto abrirá un menú interactivo:

```bash
Esto abrirá un menú interactivo:
1. Cargar datos completos
2. Cargar muestra de datos
3. Mostrar estadísticas básicas
4. Crear grafo con NetworkX
5. Analizar distribución de grado
6. Buscar usuarios más influyentes
7. Buscar usuarios por ubicación
8. Guardar datos procesados
9. Limpiar memoria
0. Salir
```

## 🔄 Flujo del Programa
1. **Carga de datos**

- Se leen las ubicaciones geográficas en chunks para optimizar el uso de memoria.
- Las conexiones entre usuarios se almacenan en un defaultdict por ID.

2. **Creación del grafo (opcional)

- Se construye un DiGraph de networkx para análisis estructurales.

3. **Análisis estructural**

- Se calcula la distribución de grado (entrada y salida).
- Se identifican los usuarios más influyentes por número de seguidores, PageRank y betweenness (si el grafo es pequeño).

4. **Análisis geográfico**

- Se calcula la distancia haversine desde un punto dado.
- Se pueden identificar usuarios dentro de un radio y sus conexiones internas.

5. **Exportación**

- Los datos procesados se pueden guardar como CSV/TXT y un resumen estadístico.

