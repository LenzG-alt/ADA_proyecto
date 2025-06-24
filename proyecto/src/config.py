# config.py
import os

# Obtener la ruta del directorio actual del script (config.py)
# Luego subir un nivel para llegar a la raíz del proyecto 'proyecto/'
# y luego entrar a 'datos/'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Esto sería proyecto/src, luego proyecto/
DATOS_DIR = os.path.join(BASE_DIR, 'datos')

DATASET_PATH = {
    'usuarios': os.path.join(DATOS_DIR, '10_million_user.txt'),
    'ubicaciones': os.path.join(DATOS_DIR, '10_million_location.txt')
}

MAX_USERS_TO_LOAD = 100_000  # Prueba con 100k usuarios primero
# CHUNK_SIZE = 10_000 # No se está usando actualmente, pero podría ser útil para pandas si se lee en chunks