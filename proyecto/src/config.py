# config.py

DATASET_PATH = {
    'usuarios': 'datos/10_million_user.txt',
    'ubicaciones': 'datos/10_million_location.txt'
}

MAX_USERS_TO_LOAD = 100_000  # Prueba con 100k usuarios primero
CHUNK_SIZE = 10_000