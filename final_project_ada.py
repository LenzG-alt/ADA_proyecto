import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import os
import time
import sys
from tqdm import tqdm
import psutil
from collections import defaultdict
import gc

class CargadorRedSocial:
    def __init__(self):
        self.ubicaciones = None
        self.conexiones = None
        self.G = None
        self.num_nodos = 0
        self.num_aristas = 0
        self.tiempo_carga = 0
    
    def cargar_ubicaciones(self, ruta_ubicaciones):
        """Carga las ubicaciones de usuarios de forma optimizada"""
        print("\nCargando ubicaciones de usuarios...")
        inicio = time.time()
        
        # Monitoreo de memoria antes de cargar
        mem_antes = psutil.Process(os.getpid()).memory_info().rss / 1024**2
        print(f"Memoria utilizada antes de cargar ubicaciones: {mem_antes:.2f} MB")
        
        # Usar dtype específico para optimizar memoria
        dtypes = {'latitud': np.float32, 'longitud': np.float32}
        
        # Carga optimizada por chunks
        chunk_size = 1000000  # 1 millón de filas por chunk
        chunks = []
        
        try:
            # Mostrar progreso por cada chunk cargado
            with tqdm(desc="Cargando chunks de ubicaciones") as pbar:
                for i, chunk in enumerate(pd.read_csv(
                    ruta_ubicaciones,
                    header=None,
                    names=['latitud', 'longitud'],
                    dtype=dtypes,
                    chunksize=chunk_size
                )):
                    chunks.append(chunk)
                    pbar.update(1)
                    
                    # Reportar uso de memoria cada 3 millones de registros
                    if (i+1) % 3 == 0:
                        mem_actual = psutil.Process(os.getpid()).memory_info().rss / 1024**2
                        print(f"  Memoria tras {(i+1)*chunk_size:,} registros: {mem_actual:.2f} MB")
            
            # Concatenar todos los chunks
            self.ubicaciones = pd.concat(chunks)
            self.num_nodos = len(self.ubicaciones)
            
        except Exception as e:
            print(f"Error al cargar ubicaciones: {e}")
            return False
        
        tiempo = time.time() - inicio
        print(f"Ubicaciones cargadas: {self.num_nodos:,} registros en {tiempo:.2f} segundos")
        
        # Reportar memoria después de cargar
        mem_despues = psutil.Process(os.getpid()).memory_info().rss / 1024**2
        print(f"Memoria utilizada después de cargar ubicaciones: {mem_despues:.2f} MB")
        print(f"Incremento de memoria: {mem_despues - mem_antes:.2f} MB")
        
        return True
    
    def cargar_conexiones(self, ruta_conexiones):
        """Carga las conexiones de usuarios (lista de adyacencia) de forma optimizada"""
        print("\nCargando conexiones de usuarios...")
        inicio = time.time()
        
        # Monitoreo de memoria antes de cargar
        mem_antes = psutil.Process(os.getpid()).memory_info().rss / 1024**2
        print(f"Memoria utilizada antes de cargar conexiones: {mem_antes:.2f} MB")
        
        # Usar defaultdict para almacenar las conexiones de forma eficiente
        self.conexiones = defaultdict(list)
        total_aristas = 0
        
        try:
            # Contar número total de líneas para la barra de progreso
            with open(ruta_conexiones, 'r') as f:
                num_lineas = sum(1 for _ in f)
            
            # Leer el archivo línea por línea (más eficiente para archivos grandes)
            with open(ruta_conexiones, 'r') as f:
                with tqdm(total=num_lineas, desc="Cargando conexiones") as pbar:
                    for i, line in enumerate(f):
                        # La i-ésima línea corresponde al usuario i+1
                        usuario_id = i + 1
                        
                        # Parsear la línea para obtener los IDs de usuarios seguidos
                        seguidos = [int(uid.strip()) for uid in line.strip().split(',') if uid.strip()]
                        self.conexiones[usuario_id] = seguidos
                        total_aristas += len(seguidos)
                        
                        pbar.update(1)
                        
                        # Reportar uso de memoria cada millón de usuarios
                        if (i+1) % 1000000 == 0:
                            mem_actual = psutil.Process(os.getpid()).memory_info().rss / 1024**2
                            print(f"  Memoria tras {i+1:,} usuarios: {mem_actual:.2f} MB")
            
            self.num_aristas = total_aristas
            
        except Exception as e:
            print(f"Error al cargar conexiones: {e}")
            return False
        
        tiempo = time.time() - inicio
        print(f"Conexiones cargadas: {len(self.conexiones):,} usuarios con {total_aristas:,} conexiones en {tiempo:.2f} segundos")
        
        # Reportar memoria después de cargar
        mem_despues = psutil.Process(os.getpid()).memory_info().rss / 1024**2
        print(f"Memoria utilizada después de cargar conexiones: {mem_despues:.2f} MB")
        print(f"Incremento de memoria: {mem_despues - mem_antes:.2f} MB")
        
        return True
    
    def cargar_datos_completos(self, ruta_ubicaciones, ruta_conexiones):
        """Carga todos los datos y muestra estadísticas"""
        print("=" * 80)
        print("INICIANDO CARGA MASIVA DE DATOS DE RED SOCIAL")
        print("=" * 80)
        
        inicio_total = time.time()
        
        # Verificar que los archivos existen
        if not os.path.exists(ruta_ubicaciones):
            print(f"ERROR: El archivo de ubicaciones no existe en la ruta: {ruta_ubicaciones}")
            return False
            
        if not os.path.exists(ruta_conexiones):
            print(f"ERROR: El archivo de conexiones no existe en la ruta: {ruta_conexiones}")
            return False
        
        # Cargar ubicaciones
        if not self.cargar_ubicaciones(ruta_ubicaciones):
            return False
        
        # Forzar recolección de basura para liberar memoria
        gc.collect()
        
        # Cargar conexiones
        if not self.cargar_conexiones(ruta_conexiones):
            return False
        
        # Calcular tiempo total
        self.tiempo_carga = time.time() - inicio_total
        
        # Mostrar resumen final
        print("\n" + "=" * 80)
        print("RESUMEN DE CARGA DE DATOS")
        print("=" * 80)
        print(f"Total de nodos (usuarios): {self.num_nodos:,}")
        print(f"Total de aristas (conexiones): {self.num_aristas:,}")
        print(f"Densidad del grafo: {self.num_aristas / (self.num_nodos * (self.num_nodos - 1)):.8f}")
        print(f"Tiempo total de carga: {self.tiempo_carga:.2f} segundos")
        
        # Mostrar uso total de memoria
        mem_total = psutil.Process(os.getpid()).memory_info().rss / 1024**2
        print(f"Memoria total utilizada: {mem_total:.2f} MB")
        
        return True
    
    def crear_grafo_networkx(self, muestra=None):
        """Crea un grafo de NetworkX a partir de los datos cargados (opcional)"""
        if self.conexiones is None:
            print("ERROR: Primero debe cargar los datos de conexiones")
            return False
        
        print("\nCreando grafo dirigido con NetworkX...")
        inicio = time.time()
        
        try:
            # Crear grafo dirigido
            self.G = nx.DiGraph()
            
            # Si se especifica una muestra, limitar el número de nodos
            if muestra is not None and muestra < len(self.conexiones):
                nodos = list(self.conexiones.keys())[:muestra]
            else:
                nodos = list(self.conexiones.keys())
            
            # Añadir nodos
            self.G.add_nodes_from(nodos)
            
            # Añadir aristas
            for nodo, conexiones in tqdm(self.conexiones.items(), desc="Añadiendo aristas"):
                if muestra is not None and nodo > muestra:
                    break
                    
                for destino in conexiones:
                    if muestra is None or destino <= muestra:
                        self.G.add_edge(nodo, destino)
            
            tiempo = time.time() - inicio
            print(f"Grafo creado con {self.G.number_of_nodes():,} nodos y {self.G.number_of_edges():,} aristas en {tiempo:.2f} segundos")
            
            return True
            
        except Exception as e:
            print(f"Error al crear grafo: {e}")
            return False
            
    def analizar_distribucion_grado(self):
        """Analiza la distribución de grado de los nodos en la red"""
        if self.conexiones is None:
            print("ERROR: Primero debe cargar los datos de conexiones")
            return False
            
        print("\nAnalizando distribución de grado de los nodos...")
        inicio = time.time()
        
        try:
            # Calcular grado de entrada (followers)
            grado_entrada = defaultdict(int)
            # Calcular grado de salida (following)
            grado_salida = {nodo: len(conexiones) for nodo, conexiones in self.conexiones.items()}
            
            # Contar grado de entrada
            print("Calculando grado de entrada (followers)...")
            for nodo, conexiones in tqdm(self.conexiones.items(), desc="Procesando conexiones"):
                for destino in conexiones:
                    grado_entrada[destino] += 1
            
            # Estadísticas de grado de entrada
            valores_entrada = list(grado_entrada.values())
            if valores_entrada:
                max_entrada = max(valores_entrada)
                min_entrada = min(valores_entrada)
                prom_entrada = sum(valores_entrada) / len(valores_entrada)
                # Nodo con más seguidores
                nodo_max_entrada = max(grado_entrada.items(), key=lambda x: x[1])[0]
            else:
                max_entrada = min_entrada = prom_entrada = 0
                nodo_max_entrada = None
            
            # Estadísticas de grado de salida
            valores_salida = list(grado_salida.values())
            if valores_salida:
                max_salida = max(valores_salida)
                min_salida = min(valores_salida)
                prom_salida = sum(valores_salida) / len(valores_salida)
                # Nodo que sigue a más usuarios
                nodo_max_salida = max(grado_salida.items(), key=lambda x: x[1])[0]
            else:
                max_salida = min_salida = prom_salida = 0
                nodo_max_salida = None
            
            tiempo = time.time() - inicio
            
            # Mostrar resultados
            print("\n" + "=" * 60)
            print("ANÁLISIS DE DISTRIBUCIÓN DE GRADO")
            print("=" * 60)
            print("Grado de entrada (followers/seguidores):")
            print(f"  - Máximo: {max_entrada:,} (Usuario ID: {nodo_max_entrada})")
            print(f"  - Mínimo: {min_entrada:,}")
            print(f"  - Promedio: {prom_entrada:.2f}")
            print("\nGrado de salida (following/seguidos):")
            print(f"  - Máximo: {max_salida:,} (Usuario ID: {nodo_max_salida})")
            print(f"  - Mínimo: {min_salida:,}")
            print(f"  - Promedio: {prom_salida:.2f}")
            print(f"\nTiempo de análisis: {tiempo:.2f} segundos")
            
            # Distribución de grado (conteo de frecuencias)
            print("\nCalculando histograma de distribución...")
            
            # Para grado de entrada
            conteo_entrada = Counter(valores_entrada)
            # Para grado de salida
            conteo_salida = Counter(valores_salida)
            
            print("\nDistribución de grado de entrada (muestra):")
            for grado, frecuencia in sorted(list(conteo_entrada.items())[:20]):
                print(f"  Grado {grado}: {frecuencia:,} nodos")
                
            print("\nDistribución de grado de salida (muestra):")
            for grado, frecuencia in sorted(list(conteo_salida.items())[:20]):
                print(f"  Grado {grado}: {frecuencia:,} nodos")
            
            return True
            
        except Exception as e:
            print(f"Error al analizar distribución de grado: {e}")
            return False
            
    def buscar_usuarios_influyentes(self, top_n=10):
        """Identifica los usuarios más influyentes basados en diferentes métricas"""
        if self.conexiones is None:
            print("ERROR: Primero debe cargar los datos de conexiones")
            return False
            
        print(f"\nBuscando los {top_n} usuarios más influyentes...")
        inicio = time.time()
        
        try:
            # Calcular grado de entrada (followers)
            grado_entrada = defaultdict(int)
            
            # Contar grado de entrada
            print("Calculando métricas de influencia...")
            for nodo, conexiones in tqdm(self.conexiones.items(), desc="Procesando conexiones"):
                for destino in conexiones:
                    grado_entrada[destino] += 1
            
            # Calcular métricas de centralidad si el grafo está disponible
            if self.G is not None:
                print("Calculando centralidad con NetworkX (puede tardar)...")
                # PageRank (algoritmo usado por Google para ranking de páginas web)
                try:
                    pagerank = nx.pagerank(self.G, alpha=0.85, max_iter=100)
                except:
                    pagerank = {}
                    print("No se pudo calcular PageRank (posible error de convergencia)")
                
                # Centralidad de intermediación (betweenness) - solo para grafos pequeños
                if self.G.number_of_nodes() < 10000:
                    betweenness = nx.betweenness_centrality(self.G, k=100, normalized=True)
                else:
                    betweenness = {}
                    print("Red demasiado grande para calcular betweenness (omitido)")
            else:
                pagerank = {}
                betweenness = {}
                print("No hay grafo disponible para cálculos de centralidades avanzadas")
            
            # Obtener Top N por grado de entrada (más followers)
            top_followers = sorted(grado_entrada.items(), key=lambda x: x[1], reverse=True)[:top_n]
            
            # Obtener Top N por PageRank
            top_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:top_n] if pagerank else []
            
            # Obtener Top N por betweenness
            top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:top_n] if betweenness else []
            
            tiempo = time.time() - inicio
            
            # Mostrar resultados
            print("\n" + "=" * 60)
            print(f"TOP {top_n} USUARIOS MÁS INFLUYENTES")
            print("=" * 60)
            
            print("\nPor número de seguidores (followers):")
            for i, (usuario, followers) in enumerate(top_followers, 1):
                print(f"  {i}. Usuario ID: {usuario} - {followers:,} seguidores")
            
            if top_pagerank:
                print("\nPor PageRank (influencia estructural):")
                for i, (usuario, score) in enumerate(top_pagerank, 1):
                    print(f"  {i}. Usuario ID: {usuario} - Score: {score:.6f}")
            
            if top_betweenness:
                print("\nPor Betweenness Centrality (intermediación):")
                for i, (usuario, score) in enumerate(top_betweenness, 1):
                    print(f"  {i}. Usuario ID: {usuario} - Score: {score:.6f}")
            
            print(f"\nTiempo de análisis: {tiempo:.2f} segundos")
            
            return True
            
        except Exception as e:
            print(f"Error al buscar usuarios influyentes: {e}")
            return False
    
    def buscar_camino_entre_usuarios(self, usuario_origen, usuario_destino, max_profundidad=4):
        """Busca el camino más corto entre dos usuarios en la red social"""
        if self.conexiones is None:
            print("ERROR: Primero debe cargar los datos de conexiones")
            return False
            
        print(f"\nBuscando camino entre Usuario {usuario_origen} y Usuario {usuario_destino}...")
        inicio = time.time()
        
        try:
            # Verificar que ambos usuarios existen en la red
            if usuario_origen not in self.conexiones:
                print(f"ERROR: El usuario {usuario_origen} no existe en la red o no tiene conexiones")
                return False
                
            if usuario_destino not in self.conexiones and usuario_destino not in [dest for conex in self.conexiones.values() for dest in conex]:
                print(f"ERROR: El usuario {usuario_destino} no existe en la red")
                return False
            
            # Si tenemos un grafo de NetworkX, usamos su algoritmo de ruta más corta
            # que es más eficiente para grafos pequeños/medianos
            if self.G is not None and usuario_origen in self.G and usuario_destino in self.G:
                print("Usando algoritmo de NetworkX para encontrar la ruta más corta...")
                try:
                    # Intentar encontrar el camino más corto
                    camino = nx.shortest_path(self.G, source=usuario_origen, target=usuario_destino)
                    
                    tiempo = time.time() - inicio
                    longitud = len(camino) - 1  # Número de conexiones = nodos - 1
                    
                    # Mostrar resultados
                    print("\n" + "=" * 60)
                    print(f"CAMINO ENCONTRADO ENTRE USUARIOS {usuario_origen} → {usuario_destino}")
                    print("=" * 60)
                    print(f"Longitud del camino: {longitud} conexiones")
                    print(f"Ruta: {' → '.join(map(str, camino))}")
                    print(f"\nTiempo de búsqueda: {tiempo:.4f} segundos")
                    
                    return camino
                except nx.NetworkXNoPath:
                    print(f"No existe un camino entre Usuario {usuario_origen} y Usuario {usuario_destino}")
                    return None
                except Exception as e:
                    print(f"Error al buscar con NetworkX: {e}")
                    print("Intentando con método de búsqueda en anchura (BFS)...")
                    # Si falla, continuamos con el método BFS manual
            
            # BFS manual para grafos muy grandes o cuando no tenemos objeto NetworkX
            print("Ejecutando búsqueda en anchura (BFS)...")
            
            # Inicializar cola de BFS con el nodo origen
            cola = [(usuario_origen, [usuario_origen])]  # (nodo, camino hasta ese nodo)
            visitados = set([usuario_origen])
            
            # Limitar profundidad máxima de búsqueda para evitar consumo excesivo de recursos
            nivel_actual = 0
            
            # Contador para monitoreo
            nodos_explorados = 0
            
            while cola:
                # Mostrar progreso cada cierto número de nodos explorados
                if nodos_explorados % 10000 == 0 and nodos_explorados > 0:
                    print(f"Nodos explorados: {nodos_explorados:,} | Nivel de profundidad: {nivel_actual}")
                
                # Extraer nodo y camino actual
                nodo_actual, camino_actual = cola.pop(0)
                nodos_explorados += 1
                
                # Si la longitud del camino supera la profundidad máxima, saltamos este nodo
                # (esto es para evitar búsquedas infinitas o muy largas)
                if len(camino_actual) > max_profundidad + 1:  # +1 porque incluye el nodo origen
                    nivel_actual = len(camino_actual) - 1
                    print(f"Alcanzada profundidad máxima ({max_profundidad}). Limitando búsqueda...")
                    continue
                
                # Actualizar nivel actual si es necesario
                if len(camino_actual) - 1 > nivel_actual:
                    nivel_actual = len(camino_actual) - 1
                    print(f"Explorando nivel {nivel_actual}...")
                
                # Si el nodo actual es el destino, hemos encontrado un camino
                if nodo_actual == usuario_destino:
                    tiempo = time.time() - inicio
                    
                    # Mostrar resultados
                    print("\n" + "=" * 60)
                    print(f"CAMINO ENCONTRADO ENTRE USUARIOS {usuario_origen} → {usuario_destino}")
                    print("=" * 60)
                    print(f"Longitud del camino: {len(camino_actual) - 1} conexiones")
                    print(f"Ruta: {' → '.join(map(str, camino_actual))}")
                    print(f"Nodos explorados: {nodos_explorados:,}")
                    print(f"\nTiempo de búsqueda: {tiempo:.4f} segundos")
                    
                    return camino_actual
                
                # Explorar vecinos (usuarios a los que sigue el usuario actual)
                if nodo_actual in self.conexiones:
                    for vecino in self.conexiones[nodo_actual]:
                        if vecino not in visitados:
                            # Crear nuevo camino añadiendo este vecino
                            nuevo_camino = camino_actual + [vecino]
                            cola.append((vecino, nuevo_camino))
                            visitados.add(vecino)
            
            # Si llegamos aquí, no se encontró camino
            tiempo = time.time() - inicio
            print(f"\nNo se encontró camino entre Usuario {usuario_origen} y Usuario {usuario_destino}")
            print(f"Nodos explorados: {nodos_explorados:,}")
            print(f"Tiempo de búsqueda: {tiempo:.4f} segundos")
            
            return None
            
        except Exception as e:
            print(f"Error al buscar camino entre usuarios: {e}")
            return None
    
    def guardar_datos_procesados(self, directorio="datos_procesados"):
        """Guarda los datos procesados para uso posterior"""
        if self.ubicaciones is None and self.conexiones is None:
            print("ERROR: No hay datos para guardar")
            return False
            
        print(f"\nGuardando datos procesados en directorio: {directorio}")
        inicio = time.time()
        
        try:
            # Crear directorio si no existe
            if not os.path.exists(directorio):
                os.makedirs(directorio)
                print(f"Directorio '{directorio}' creado")
            
            # Guardar ubicaciones si existen
            if self.ubicaciones is not None:
                ruta_ubicaciones = os.path.join(directorio, "ubicaciones_procesadas.csv")
                self.ubicaciones.to_csv(ruta_ubicaciones, index=False)
                print(f"Ubicaciones guardadas en: {ruta_ubicaciones}")
            
            # Guardar conexiones si existen
            if self.conexiones is not None:
                ruta_conexiones = os.path.join(directorio, "conexiones_procesadas.txt")
                with open(ruta_conexiones, 'w') as f:
                    for usuario, conexiones in tqdm(self.conexiones.items(), desc="Guardando conexiones"):
                        f.write(f"{usuario}: {','.join(map(str, conexiones))}\n")
                print(f"Conexiones guardadas en: {ruta_conexiones}")
            
            # Guardar estadísticas básicas
            ruta_estadisticas = os.path.join(directorio, "estadisticas_red.txt")
            with open(ruta_estadisticas, 'w') as f:
                f.write(f"Total de nodos (usuarios): {self.num_nodos:,}\n")
                f.write(f"Total de aristas (conexiones): {self.num_aristas:,}\n")
                f.write(f"Densidad del grafo: {self.num_aristas / (self.num_nodos * (self.num_nodos - 1)):.8f}\n")
                f.write(f"Tiempo de carga: {self.tiempo_carga:.2f} segundos\n")
            print(f"Estadísticas guardadas en: {ruta_estadisticas}")
            
            tiempo = time.time() - inicio
            print(f"\nTodos los datos guardados en {tiempo:.2f} segundos")
            
            return True
            
        except Exception as e:
            print(f"Error al guardar datos: {e}")
            return False

def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "=" * 50)
    print("MENÚ DE ANÁLISIS DE RED SOCIAL")
    print("=" * 50)
    print("1. Cargar datos completos (10 millones de usuarios)")
    print("2. Cargar muestra de datos (especificar tamaño)")
    print("3. Mostrar estadísticas básicas")
    print("4. Crear grafo con NetworkX (solo con muestra)")
    print("5. Analizar distribución de grado")
    print("6. Buscar usuarios más influyentes")
    print("7. Buscar camino entre dos usuarios")
    print("8. Guardar datos procesados")
    print("9. Limpiar memoria")
    print("0. Salir")
    print("=" * 50)

def ejecutar_menu():
    """Ejecuta el menú interactivo"""
    cargador = CargadorRedSocial()
    opcion = -1
    
    # Rutas por defecto (ajustar según sea necesario)
    ruta_ubicaciones = "10_million_location.txt"
    ruta_conexiones = "10_million_user.txt"
    
    while opcion != 0:
        mostrar_menu()
        try:
            opcion = int(input("\nSeleccione una opción: "))
            
            if opcion == 1:
                # Cargar datos completos
                cargador.cargar_datos_completos(ruta_ubicaciones, ruta_conexiones)
                
            elif opcion == 2:
                # Cargar muestra de datos
                try:
                    tamaño = int(input("Ingrese el tamaño de la muestra (número de usuarios): "))
                    if tamaño <= 0:
                        print("ERROR: El tamaño debe ser un número positivo")
                        continue
                        
                    # Implementar carga parcial
                    print(f"Cargando muestra de {tamaño:,} usuarios...")
                    # Aquí implementar la carga parcial
                    
                except ValueError:
                    print("ERROR: Debe ingresar un número válido")
                
            elif opcion == 3:
                # Mostrar estadísticas básicas
                if cargador.num_nodos == 0:
                    print("ERROR: Primero debe cargar los datos")
                    continue
                    
                print("\n" + "=" * 50)
                print("ESTADÍSTICAS BÁSICAS DE LA RED")
                print("=" * 50)
                print(f"Total de nodos (usuarios): {cargador.num_nodos:,}")
                print(f"Total de aristas (conexiones): {cargador.num_aristas:,}")
                print(f"Densidad del grafo: {cargador.num_aristas / (cargador.num_nodos * (cargador.num_nodos - 1)):.8f}")
                
                # Mostrar más estadísticas si el grafo está creado
                if cargador.G is not None:
                    print(f"Diámetro del grafo (muestra): {nx.diameter(cargador.G)}")
                    print(f"Longitud media del camino más corto: {nx.average_shortest_path_length(cargador.G):.4f}")
                
            elif opcion == 4:
                # Crear grafo con NetworkX y visualizarlo (solo con muestra)
                if cargador.conexiones is None:
                    print("ERROR: Primero debe cargar los datos de conexiones")
                    continue
                    
                try:
                    tamaño = int(input("Ingrese el tamaño de la muestra para el grafo (recomendado <1000 para visualización): "))
                    if tamaño <= 0:
                        print("ERROR: El tamaño debe ser un número positivo")
                        continue
                        
                    if tamaño > 1000:
                        confirmar = input(f"ADVERTENCIA: Visualizar un grafo con {tamaño:,} nodos puede ser lento y difícil de interpretar. ¿Continuar? (s/n): ")
                        if confirmar.lower() != 's':
                            continue
                    
                    # Crear el grafo con el tamaño especificado
                    if not cargador.crear_grafo_networkx(tamaño):
                        print("ERROR: No se pudo crear el grafo")
                        continue
                    
                    # Depuración: Verificar Python y matplotlib
                    import sys
                    print(f"Versión de Python: {sys.version}")
                    print(f"Ruta del ejecutable: {sys.executable}")
                    try:
                        import matplotlib
                        print(f"Versión de Matplotlib: {matplotlib.__version__}")
                    except ImportError as e:
                        print(f"Error al importar matplotlib: {e}")
                        raise
                    
                    # Importar matplotlib para visualización
                    import matplotlib.pyplot as plt
                    
                    print("\nGenerando visualización del grafo...")
                    
                    # Configurar el diseño del grafo
                    plt.figure(figsize=(12, 8))
                    pos = nx.spring_layout(cargador.G, k=1.5/np.sqrt(cargador.G.number_of_nodes()), iterations=50)
                    nx.draw_networkx_nodes(cargador.G, pos, node_size=50, node_color='lightblue', alpha=0.7)
                    nx.draw_networkx_edges(cargador.G, pos, alpha=0.3)
                    
                    if tamaño <= 100:
                        nx.draw_networkx_labels(cargador.G, pos, font_size=8)
                    
                    plt.title(f"Grafo de Red Social (Muestra de {cargador.G.number_of_nodes():,} nodos)")
                    plt.axis('off')
                    plt.tight_layout()
                    plt.show()
                    
                    print(f"Visualización generada con {cargador.G.number_of_nodes():,} nodos y {cargador.G.number_of_edges():,} aristas")
                    
                except ValueError:
                    print("ERROR: Debe ingresar un número válido")
                except ImportError as e:
                    print(f"ERROR: Problema con Matplotlib: {e}")
                    print("Asegúrate de que matplotlib esté instalado en el entorno correcto.")
                    print("Intenta ejecutar: python -m pip install matplotlib")
                except Exception as e:
                    print(f"ERROR al generar la visualización: {e}")
            elif opcion == 5:
                # Analizar distribución de grado
                if cargador.conexiones is None:
                    print("ERROR: Primero debe cargar los datos de conexiones")
                    continue
                    
                cargador.analizar_distribucion_grado()
                
            elif opcion == 6:
                # Buscar usuarios más influyentes
                if cargador.conexiones is None:
                    print("ERROR: Primero debe cargar los datos de conexiones")
                    continue
                
                try:
                    top_n = int(input("Ingrese el número de usuarios influyentes a mostrar: "))
                    if top_n <= 0:
                        print("ERROR: El número debe ser positivo")
                        continue
                        
                    cargador.buscar_usuarios_influyentes(top_n)
                    
                except ValueError:
                    print("ERROR: Debe ingresar un número válido")
                
            elif opcion == 7:
                # Buscar camino entre dos usuarios
                if cargador.conexiones is None:
                    print("ERROR: Primero debe cargar los datos de conexiones")
                    continue
                
                try:
                    usuario_origen = int(input("Ingrese el ID del usuario de origen: "))
                    usuario_destino = int(input("Ingrese el ID del usuario de destino: "))
                    
                    if usuario_origen <= 0 or usuario_destino <= 0:
                        print("ERROR: Los IDs de usuario deben ser positivos")
                        continue
                        
                    # Solicitar la profundidad máxima de búsqueda
                    max_profundidad = int(input("Ingrese la profundidad máxima de búsqueda (recomendado 3-6): "))
                    if max_profundidad <= 0:
                        print("ERROR: La profundidad debe ser positiva")
                        continue
                    elif max_profundidad > 8:
                        confirmar = input(f"ADVERTENCIA: Una profundidad de {max_profundidad} puede tardar mucho tiempo. ¿Continuar? (s/n): ")
                        if confirmar.lower() != 's':
                            continue
                    
                    cargador.buscar_camino_entre_usuarios(usuario_origen, usuario_destino, max_profundidad)
                    
                except ValueError:
                    print("ERROR: Debe ingresar IDs de usuario válidos")
                
            elif opcion == 8:
                # Guardar datos procesados
                if cargador.ubicaciones is None and cargador.conexiones is None:
                    print("ERROR: No hay datos para guardar")
                    continue
                
                directorio = input("Ingrese el directorio para guardar los datos (default: datos_procesados): ")
                if not directorio:
                    directorio = "datos_procesados"
                    
                cargador.guardar_datos_procesados(directorio)
                
            elif opcion == 9:
                # Limpiar memoria
                del cargador.G
                cargador.G = None
                gc.collect()
                print("Memoria limpiada. El grafo ha sido eliminado.")
                
            elif opcion == 0:
                print("Saliendo del programa...")
                
            else:
                print("Opción no válida. Intente de nuevo.")
                
        except ValueError:
            print("ERROR: Debe ingresar un número válido")
        
        except Exception as e:
            print(f"ERROR inesperado: {e}")
            
        # Pausa antes de volver al menú
        if opcion != 0:
            input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 2:
        ruta_ubicaciones = sys.argv[1]
        ruta_conexiones = sys.argv[2]
        print(f"Usando archivos: {ruta_ubicaciones} y {ruta_conexiones}")
        
        # Crear cargador y cargar datos directamente
        cargador = CargadorRedSocial()
        cargador.cargar_datos_completos(ruta_ubicaciones, ruta_conexiones)
        
        # Mostrar menú interactivo
        ejecutar_menu()
    else:
        # Iniciar menú interactivo
        ejecutar_menu()
