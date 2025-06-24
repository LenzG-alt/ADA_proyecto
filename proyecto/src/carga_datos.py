# carga_datos.py
import pandas as pd
import numpy as np
import logging
from utils import medir_tiempo, ValidadorDatos

@medir_tiempo
def cargar_usuarios(ruta_archivo: str, max_lineas: int) -> list:
    """
    Carga conexiones de usuarios desde un archivo .txt.
    Cada línea representa un usuario y contiene una lista de IDs de usuarios a los que sigue,
    separados por comas.
    Se procesarán como máximo `max_lineas` usuarios.
    Los IDs se validan para asegurar que sean enteros y se limpian.
    """
    logging.info(f"Iniciando carga de conexiones de usuarios desde: {ruta_archivo} (max_lineas={max_lineas})")
    conexiones_por_usuario = []
    usuarios_procesados = 0
    lineas_con_error = 0

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            for i, linea in enumerate(f):
                if usuarios_procesados >= max_lineas:
                    logging.info(f"Alcanzado el límite de {max_lineas} usuarios a cargar.")
                    break

                linea_strip = linea.strip()
                if not linea_strip: # Ignorar líneas vacías
                    conexiones_por_usuario.append([]) # Usuario sin conexiones salientes
                    usuarios_procesados += 1
                    continue

                try:
                    # Convertir IDs a enteros. No se valida el rango aquí, se hará después
                    # si es necesario, una vez que se conozca el tamaño total del grafo.
                    amigos_str = linea_strip.split(',')
                    amigos_int = []
                    for amigo_s in amigos_str:
                        try:
                            amigos_int.append(int(amigo_s))
                        except ValueError:
                            # logging.debug(f"Línea {i+1}, usuario {usuarios_procesados}: ID de amigo no entero '{amigo_s}' omitido.")
                            pass # Omitir IDs no válidos discretamente o registrar con debug

                    conexiones_por_usuario.append(amigos_int)
                except Exception as e:
                    logging.error(f"Error procesando línea {i+1} (usuario {usuarios_procesados}): '{linea_strip}'. Error: {e}")
                    conexiones_por_usuario.append([]) # Añadir lista vacía en caso de error en la línea
                    lineas_con_error += 1

                usuarios_procesados += 1

    except FileNotFoundError:
        logging.error(f"Archivo de usuarios no encontrado en la ruta: {ruta_archivo}")
        return []
    except Exception as e:
        logging.error(f"Error general al leer el archivo de usuarios {ruta_archivo}: {e}")
        return []

    logging.info(f"Carga de usuarios completada. Usuarios procesados: {usuarios_procesados}. Líneas con error (formato): {lineas_con_error}.")

    return conexiones_por_usuario


@medir_tiempo
def cargar_ubicaciones(ruta_archivo: str, max_lineas: int) -> list:
    """
    Carga datos de ubicación (latitud, longitud) desde un archivo CSV.
    Se procesarán como máximo `max_lineas` ubicaciones.
    Valida que las coordenadas estén en rangos válidos.
    """
    logging.info(f"Iniciando carga de ubicaciones desde: {ruta_archivo} (max_lineas={max_lineas})")
    ubicaciones_validas = []
    filas_leidas = 0

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            for i, linea in enumerate(f):
                if i >= max_lineas:
                    logging.info(f"Alcanzado el límite de {max_lineas} ubicaciones a leer.")
                    break
                filas_leidas +=1
                linea_strip = linea.strip()
                if not linea_strip:
                    continue

                partes = linea_strip.split(',')
                if len(partes) == 2:
                    lat_str, lon_str = partes[0], partes[1]
                    try:
                        lat = float(lat_str)
                        lon = float(lon_str)
                        if ValidadorDatos.validar_coordenadas(lat, lon):
                            ubicaciones_validas.append((np.float32(lat), np.float32(lon)))
                        # else: La validación ya loggea
                        #     logging.warning(f"Línea {i+1}: Coordenadas ({lat_str}, {lon_str}) fuera de rango, omitidas.")
                    except ValueError:
                        logging.warning(f"Línea {i+1}: No se pudieron convertir coordenadas '{lat_str}', '{lon_str}' a float. Omitida.")
                else:
                    logging.warning(f"Línea {i+1}: Formato incorrecto '{linea_strip}'. Se esperaban 2 valores separados por coma. Omitida.")

        num_ubicaciones_validas = len(ubicaciones_validas)
        logging.info(f"Carga de ubicaciones completada. Filas leídas del archivo: {filas_leidas}. Ubicaciones válidas procesadas: {num_ubicaciones_validas}.")

    except FileNotFoundError:
        logging.error(f"Archivo de ubicaciones no encontrado en la ruta: {ruta_archivo}")
        return []
    except Exception as e:
        # Captura más genérica para otros posibles errores de lectura/procesamiento
        logging.error(f"Error general al leer o procesar el archivo de ubicaciones {ruta_archivo}: {e}")
        return []

    return ubicaciones_validas