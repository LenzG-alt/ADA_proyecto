# geografia.py
import matplotlib.pyplot as plt
import os
import logging
from utils import medir_tiempo

BASE_GRAFICOS_PATH = "resultados/graficos/geograficos"

def _preparar_directorio_graficos():
    os.makedirs(BASE_GRAFICOS_PATH, exist_ok=True)

@medir_tiempo
def graficar_distribucion_geografica(ubicaciones: list, nombre_archivo="distribucion_geografica_usuarios.png"):
    """
    Grafica la distribución geográfica de los usuarios (latitud vs longitud).
    """
    _preparar_directorio_graficos()

    if not ubicaciones:
        logging.warning("No hay datos de ubicación para graficar.")
        return

    try:
        # Desempaquetar latitudes y longitudes
        # Filtrar posibles None si la carga de datos no los eliminó (aunque debería)
        lats = [u[0] for u in ubicaciones if u and len(u) == 2 and isinstance(u[0], (int, float))]
        lons = [u[1] for u in ubicaciones if u and len(u) == 2 and isinstance(u[1], (int, float))]

        if not lats or not lons:
            logging.warning("No hay suficientes datos de latitud/longitud válidos para graficar.")
            return

        plt.figure(figsize=(12, 8))
        plt.scatter(lons, lats, s=1, alpha=0.2, color='dodgerblue', edgecolor='none') # s=tamaño, alpha=transparencia

        plt.title("Distribución Geográfica de Usuarios")
        plt.xlabel("Longitud")
        plt.ylabel("Latitud")

        # Añadir límites geográficos estándar para referencia
        plt.xlim(-180, 180)
        plt.ylim(-90, 90)

        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout() # Ajustar para que no se corten etiquetas

        ruta_completa = os.path.join(BASE_GRAFICOS_PATH, nombre_archivo)
        plt.savefig(ruta_completa)
        plt.close() # Cerrar la figura para liberar memoria
        logging.info(f"Gráfico de distribución geográfica guardado en {ruta_completa}")

    except Exception as e:
        logging.error(f"Error al generar el gráfico de distribución geográfica: {e}")

# Podrían añadirse más funciones geográficas aquí, como:
# - Graficar usuarios en un mapa real (usando bibliotecas como GeoPandas, Folium, Plotly Express)
# - Calcular densidad de usuarios por región
# - Analizar distancia promedio entre usuarios conectados (si tiene sentido para el proyecto)