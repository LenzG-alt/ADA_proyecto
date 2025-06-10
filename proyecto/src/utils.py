import logging
import time
from typing import List, Any
# utils.py

def setup_logger():
    """Configura un logger para registrar eventos y tiempos de ejecución."""
    logging.basicConfig(
        filename='registro.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# Configuración de logs
logging.basicConfig(
    filename="registro.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Decorador para medir tiempos
def medir_tiempo(func):
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fin = time.time()
        logging.info(f"Ejecutando {func.__name__}: {fin - inicio:.2f}s")
        return resultado
    return wrapper

# Clase para validar datos
class ValidadorDatos:
    @staticmethod
    def validar_usuario(usuario_id: int, rango_max: int) -> bool:
        return 0 <= usuario_id < rango_max

    @staticmethod
    def validar_coordenada(lat: float, lon: float) -> bool:
        return -90 <= lat <= 90 and -180 <= lon <= 180

    @staticmethod
    def limpiar_lista(lista: List[Any]) -> List[Any]:
        return [x for x in lista if x is not None]