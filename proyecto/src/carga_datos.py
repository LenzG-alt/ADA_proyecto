# carga_datos.py
import pandas as pd
import numpy as np
import logging
from tqdm import tqdm
from utils import medir_tiempo, ValidadorDatos

@medir_tiempo
def cargar_usuarios(ruta_archivo: str, max_lineas: int, chunk_size: int = 100000) -> list:
    """
    Carga conexiones de usuarios desde un archivo .txt.
    Cada línea representa un usuario y contiene una lista de IDs de usuarios a los que sigue,
    separados por comas.
    Se procesarán como máximo `max_lineas` usuarios.
    Los IDs se validan para asegurar que sean enteros y se limpian.
    El archivo se procesa en trozos de `chunk_size` líneas.
    """
    logging.info(f"Iniciando carga de conexiones de usuarios desde: {ruta_archivo} (max_lineas={max_lineas}, chunk_size={chunk_size})")
    conexiones_por_usuario = []
    usuarios_procesados_total = 0
    lineas_con_error_total = 0
    eof = False

    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f, \
             tqdm(total=max_lineas, desc="Cargando usuarios", unit="usuarios", disable=logging.getLogger().level > logging.INFO) as pbar:
            while not eof and usuarios_procesados_total < max_lineas:
                chunk_lines = []
                # Leer un chunk de líneas sin exceder max_lineas en total
                for _ in range(chunk_size):
                    if usuarios_procesados_total + len(chunk_lines) >= max_lineas:
                        break
                    try:
                        linea = next(f)
                        chunk_lines.append(linea)
                    except StopIteration:
                        eof = True
                        break

                if not chunk_lines and eof:
                    # logging.info("Fin de archivo alcanzado al intentar leer un nuevo chunk.") # Log más específico
                    break

                # logging.debug(f"Procesando chunk de {len(chunk_lines)} líneas. Total procesados antes: {usuarios_procesados_total}")

                for linea_idx, linea in enumerate(chunk_lines):
                    # Este chequeo es vital para no procesar más allá de max_lineas
                    # si el chunk leído nos llevaría más allá.
                    if usuarios_procesados_total >= max_lineas:
                        # logging.info(f"Alcanzado el límite de {max_lineas} usuarios a cargar dentro de un chunk.")
                        break

                    linea_strip = linea.strip()
                    # current_line_number_in_file = usuarios_procesados_total + 1

                    if not linea_strip:
                        conexiones_por_usuario.append([])
                        # No se incrementa pbar aquí si contamos usuarios con conexiones.
                        # O sí, si contamos cada línea como un intento de usuario.
                        # Decidimos actualizar pbar por cada línea procesada que podría ser un usuario.
                    else:
                        try:
                            amigos_str = linea_strip.split(',')
                            amigos_int = []
                            for amigo_s in amigos_str:
                                try:
                                    amigos_int.append(int(amigo_s))
                                except ValueError:
                                    pass
                            conexiones_por_usuario.append(amigos_int)
                        except Exception as e:
                            # logging.error(f"Error procesando línea global aprox. {current_line_number_in_file} (usuario {usuarios_procesados_total}): '{linea_strip}'. Error: {e}")
                            conexiones_por_usuario.append([])
                            lineas_con_error_total += 1

                    usuarios_procesados_total += 1
                    pbar.update(1) # Actualizar la barra de progreso por cada usuario procesado

                # Salir del bucle while si max_lineas se alcanzó después de procesar el chunk.
                if usuarios_procesados_total >= max_lineas:
                    # logging.info(f"Alcanzado el límite de {max_lineas} usuarios después de procesar un chunk.")
                    break

            # Asegurarse de que la barra de progreso refleje el total real si se detuvo antes.
            pbar.n = usuarios_procesados_total
            pbar.refresh()

            if eof and usuarios_procesados_total < max_lineas:
                logging.info(f"Fin de archivo alcanzado antes de llegar a max_lineas. Usuarios procesados: {usuarios_procesados_total}")
            elif usuarios_procesados_total >= max_lineas:
                logging.info(f"Alcanzado el límite de {max_lineas} usuarios. Total procesados: {usuarios_procesados_total}")



    except FileNotFoundError:
        logging.error(f"Archivo de usuarios no encontrado en la ruta: {ruta_archivo}")
        return []
    except Exception as e:
        logging.error(f"Error general al leer el archivo de usuarios {ruta_archivo}: {e}")
        return []

    logging.info(f"Carga de usuarios completada. Usuarios procesados en total: {usuarios_procesados_total}. Líneas con error (formato): {lineas_con_error_total}.")

    return conexiones_por_usuario


@medir_tiempo
def cargar_ubicaciones(ruta_archivo: str, max_lineas: int, chunk_size: int = 100000) -> list:
    """
    Carga datos de ubicación (latitud, longitud) desde un archivo CSV.
    Se procesarán como máximo `max_lineas` ubicaciones.
    Valida que las coordenadas estén en rangos válidos.
    El archivo se procesa en trozos utilizando pandas.
    """
    logging.info(f"Iniciando carga de ubicaciones desde: {ruta_archivo} (max_lineas={max_lineas}, chunk_size={chunk_size})")
    ubicaciones_validas = []
    filas_procesadas_total = 0
    num_ubicaciones_validas_inicial = 0

    try:
        # Iterador para pd.read_csv con chunksize
        iterador_chunks = pd.read_csv(
            ruta_archivo, header=None, names=['lat', 'lon'],
            chunksize=chunk_size, encoding='utf-8',
            on_bad_lines='warn', dtype_backend='numpy_nullable'
        )

        with tqdm(total=max_lineas, desc="Cargando ubicaciones", unit="ubicaciones", disable=logging.getLogger().level > logging.INFO) as pbar:
            for chunk_df in iterador_chunks:
                if filas_procesadas_total >= max_lineas:
                    # logging.info(f"Alcanzado el límite de {max_lineas} ubicaciones a procesar antes de un nuevo chunk.")
                    break

                filas_a_procesar_en_este_chunk = max_lineas - filas_procesadas_total

                # Si el chunk actual es más grande que las filas restantes permitidas, tomar solo las necesarias.
                if len(chunk_df) > filas_a_procesar_en_este_chunk:
                    chunk_df_a_procesar = chunk_df.head(filas_a_procesar_en_este_chunk)
                else:
                    chunk_df_a_procesar = chunk_df

                # logging.debug(f"Procesando chunk de hasta {len(chunk_df_a_procesar)} filas para ubicaciones. Total procesadas hasta ahora: {filas_procesadas_total}")

                for index, row in chunk_df_a_procesar.iterrows():
                    # Doble chequeo, aunque head() debería haber limitado el DataFrame
                    if filas_procesadas_total >= max_lineas:
                        break

                    try:
                        lat_val = row['lat']
                        lon_val = row['lon']

                        if pd.isna(lat_val) or pd.isna(lon_val):
                            # logging.warning(f"Fila {filas_procesadas_total + 1} (índice pandas {index}): Coordenadas contienen NA ('{lat_val}', '{lon_val}'). Omitida.")
                            pass # Simplemente se omite, no se cuenta como válida
                        else:
                            lat = float(lat_val)
                            lon = float(lon_val)
                            if ValidadorDatos.validar_coordenadas(lat, lon):
                                ubicaciones_validas.append((np.float32(lat), np.float32(lon)))

                    except ValueError:
                        # logging.warning(f"Fila {filas_procesadas_total + 1} (índice pandas {index}): No se pudieron convertir coordenadas '{row['lat']}', '{row['lon']}' a float. Omitida.")
                        pass # Se omite
                    except Exception as e:
                        # logging.error(f"Fila {filas_procesadas_total + 1} (índice pandas {index}): Error procesando fila: {row.to_dict()}. Error: {e}. Omitida.")
                        pass # Se omite

                    filas_procesadas_total += 1
                    pbar.update(1) # Actualizar la barra por cada fila intentada del chunk

                if filas_procesadas_total >= max_lineas:
                    # logging.info(f"Alcanzado el límite de {max_lineas} ubicaciones después de procesar un chunk.")
                    break

            pbar.n = filas_procesadas_total
            pbar.refresh()

            num_ubicaciones_cargadas_final = len(ubicaciones_validas)
            logging.info(f"Carga de ubicaciones completada. Filas totales intentadas procesar: {filas_procesadas_total}. Ubicaciones válidas cargadas: {num_ubicaciones_cargadas_final}.")

    except FileNotFoundError:
        logging.error(f"Archivo de ubicaciones no encontrado en la ruta: {ruta_archivo}")
        return []
    except pd.errors.EmptyDataError: # Especificar error de pandas para archivo vacío
        logging.warning(f"El archivo de ubicaciones {ruta_archivo} está vacío o no contiene datos procesables por pandas.")
        return []
    except Exception as e:
        logging.error(f"Error general al leer o procesar el archivo de ubicaciones {ruta_archivo} con pandas: {e}")
        return []

    return ubicaciones_validas