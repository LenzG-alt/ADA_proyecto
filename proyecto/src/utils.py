# utils.py
import logging
import time
from typing import List, Any, Callable
import os

# Configuración de directorios de resultados
BASE_RESULTADOS_PATH = "resultados"
LOG_FILE_PATH = os.path.join(BASE_RESULTADOS_PATH, "registro_analisis.log")

def setup_logger():
    """Configura un logger para registrar eventos y tiempos de ejecución."""
    os.makedirs(BASE_RESULTADOS_PATH, exist_ok=True) # Asegura que el directorio de resultados exista

    # Evitar añadir múltiples handlers si la función se llama varias veces
    logger = logging.getLogger()
    if not logger.handlers: # Solo configurar si no hay handlers existentes
        logger.setLevel(logging.INFO)

        # Formato del log
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s')

        # Handler para archivo
        file_handler = logging.FileHandler(LOG_FILE_PATH, mode='w') # 'w' para sobrescribir en cada ejecución
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Handler para consola (opcional, pero útil para debugging interactivo)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        # console_handler.setLevel(logging.DEBUG) # Podría ser más verboso en consola
        logger.addHandler(console_handler)

        logging.info("Logger configurado.")
    else:
        logging.info("Logger ya configurado.")


# Decorador para medir tiempos
def medir_tiempo(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        nombre_func = func.__name__
        logging.debug(f"Iniciando ejecución de {nombre_func}...")
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fin = time.time()
        tiempo_transcurrido = fin - inicio
        # Loguear siempre al archivo
        logging.info(f"Función {nombre_func} completada en {tiempo_transcurrido:.4f} segundos.")
        # Imprimir en consola si el logger principal está en INFO o superior
        # Esto evita duplicar mensajes si la consola ya muestra los logs INFO.
        # Sin embargo, para asegurar que se vea en consola independientemente de la configuración del handler de consola,
        # podemos imprimir directamente, o usar un logger específico para esto.
        # Por simplicidad, imprimiremos directamente un mensaje formateado.
        print(f"[INFO] {nombre_func} tomó {tiempo_transcurrido:.2f}s")
        return resultado
    return wrapper

# Clase para validar datos (puede expandirse)
class ValidadorDatos:
    @staticmethod
    def validar_id_usuario(usuario_id: Any, rango_max: int) -> bool:
        if not isinstance(usuario_id, int):
            logging.warning(f"ID de usuario '{usuario_id}' no es un entero.")
            return False
        if not (0 <= usuario_id < rango_max):
            logging.warning(f"ID de usuario {usuario_id} fuera del rango esperado (0-{rango_max-1}).")
            return False
        return True

    @staticmethod
    def validar_coordenadas(lat: Any, lon: Any) -> bool:
        try:
            lat_f = float(lat)
            lon_f = float(lon)
            if not (-90 <= lat_f <= 90 and -180 <= lon_f <= 180):
                logging.warning(f"Coordenadas ({lat_f}, {lon_f}) fuera de rango.")
                return False
            return True
        except (ValueError, TypeError):
            logging.warning(f"Coordenadas ('{lat}', '{lon}') no son números válidos.")
            return False

    @staticmethod
    def limpiar_lista_conexiones(lista_conexiones: List[List[Any]], num_total_nodos: int) -> List[List[int]]:
        """
        Limpia la lista de conexiones:
        - Asegura que todos los IDs sean enteros.
        - Filtra IDs que estén fuera del rango de nodos válidos.
        - Elimina duplicados dentro de la lista de amigos de cada usuario.
        """
        conexiones_limpias = []
        for i, amigos in enumerate(lista_conexiones):
            amigos_limpios_validos = []
            if not isinstance(amigos, list):
                logging.warning(f"Usuario {i}: lista de amigos no es una lista, se omite. Valor: {amigos}")
                conexiones_limpias.append([]) # Mantener la estructura de lista de listas
                continue

            for amigo_id in amigos:
                try:
                    id_val = int(amigo_id)
                    if 0 <= id_val < num_total_nodos: # Validar contra el número total de nodos
                        amigos_limpios_validos.append(id_val)
                    # else:
                        # logging.debug(f"Usuario {i}: amigo ID {id_val} fuera de rango (0-{num_total_nodos-1}).")
                except (ValueError, TypeError):
                    # logging.debug(f"Usuario {i}: amigo ID '{amigo_id}' no es un entero válido.")
                    pass # Simplemente se omite el amigo no válido

            # Eliminar duplicados manteniendo el orden (si es importante) o usando set para eficiencia
            conexiones_limpias.append(list(dict.fromkeys(amigos_limpios_validos)))
        return conexiones_limpias