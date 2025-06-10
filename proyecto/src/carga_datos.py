# carga_datos.py

import pandas as pd
import numpy as np

def cargar_usuarios(ruta, max_users=100_000):
    """
    Carga conexiones de usuarios desde un archivo .txt
    donde cada línea contiene los IDs de los usuarios que sigue.
    """
    conexiones = []
    with open(ruta, 'r', encoding='utf-8') as f:
        for i, linea in enumerate(f):
            if i >= max_users:
                break
            try:
                amigos = list(map(int, linea.strip().split(',')))
                conexiones.append(amigos)
            except Exception as e:
                print(f"Error al procesar línea {i}: {e}")
    return conexiones


def cargar_ubicaciones(ruta, max_users=100_000):
    """
    Carga latitud y longitud usando pandas con tipos optimizados.
    """
    dtypes = {"lat": np.float32, "lon": np.float32}
    df = pd.read_csv(
        ruta,
        delimiter=",",
        nrows=max_users,
        header=None,
        names=["lat", "lon"],
        dtype=dtypes,
        engine="c"
    )
    return df[["lat", "lon"]].values.tolist()