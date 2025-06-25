# data_generator.py
import random
import sys

# data_generator.py
import random
import sys

DEFAULT_NUM_USERS = 100 # Default para ejecuciones en el entorno Aider
# Si deseas probar con más usuarios localmente, puedes ejecutar:
# python data_generator.py <numero_de_usuarios>
# Por ejemplo: python data_generator.py 10000

NUM_USERS_CMD_ARG = None

# Esta lógica se ejecuta cuando el script se carga/importa.
# Si se ejecuta como script principal, intenta leer argumentos de línea de comandos.
if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            NUM_USERS_CMD_ARG = int(sys.argv[1])
            print(f"Data generator: NUM_USERS set to {NUM_USERS_CMD_ARG} from command line argument.")
        except ValueError:
            print(f"Warning: Invalid command line argument '{sys.argv[1]}' for NUM_USERS. Defaulting to {DEFAULT_NUM_USERS}.")
            NUM_USERS_CMD_ARG = DEFAULT_NUM_USERS
    else:
        # No imprimir el mensaje de default si es importado, solo si se ejecuta directamente.
        print(f"Data generator: NUM_USERS defaulting to {DEFAULT_NUM_USERS}. Pass an integer argument to change when running script directly.")
        NUM_USERS_CMD_ARG = DEFAULT_NUM_USERS

# NUM_USERS será el valor global importable.
# Si el script no es __main__ (es decir, es importado), NUM_USERS_CMD_ARG será None,
# y NUM_USERS tomará el DEFAULT_NUM_USERS.
# Si es __main__, NUM_USERS tomará el valor de la línea de comandos o el default.
NUM_USERS = NUM_USERS_CMD_ARG if NUM_USERS_CMD_ARG is not None else DEFAULT_NUM_USERS
MAX_CONNECTIONS_PER_USER = 5


def generate_location_data(filename="simulated_locations.txt", num_users_to_generate=None):
    """
    Genera datos de ubicación simulados (latitud, longitud).
    Escribe línea por línea para eficiencia de memoria.
    """
    # Usar el NUM_USERS global si num_users_to_generate no se especifica.
    # Esto permite que main.py importe NUM_USERS y lo use, o que este script
    # use el valor de la línea de comandos si se ejecuta directamente.
    actual_num_users = num_users_to_generate if num_users_to_generate is not None else NUM_USERS

    # Solo imprimir mensajes de generación si el script se ejecuta directamente.
    if __name__ == "__main__":
        print(f"Generating {filename} for {actual_num_users} users...")

    count = 0
    with open(filename, "w") as f:
        for _ in range(actual_num_users):
            lat = random.uniform(-90, 90)
            lon = random.uniform(-180, 180)
            f.write(f"{lat:.6f},{lon:.6f}\n")
            count +=1
            if actual_num_users > 10000 and count % (actual_num_users // 100) == 0:
                 if __name__ == "__main__": # Solo mostrar progreso si se ejecuta directamente
                    progress = (count / actual_num_users) * 100
                    sys.stdout.write(f"\rGenerated location data: {progress:.2f}% complete ({count}/{actual_num_users})")
                    sys.stdout.flush()

    if actual_num_users > 10000 and __name__ == "__main__":
        sys.stdout.write("\n")
    if __name__ == "__main__":
        print(f"Finished generating {filename} with {count} users.")


def generate_user_data(filename="simulated_users.txt", num_users_to_generate=None):
    """
    Genera datos de conexiones de usuarios simulados (lista de adyacencia).
    Los IDs de usuario comienzan en 1. Escribe línea por línea.
    """
    actual_num_users = num_users_to_generate if num_users_to_generate is not None else NUM_USERS
    if __name__ == "__main__":
        print(f"Generating {filename} for {actual_num_users} users...")

    count = 0
    with open(filename, "w") as f:
        for i in range(1, actual_num_users + 1):
            max_conn_this_user = min(MAX_CONNECTIONS_PER_USER, actual_num_users - 1 if actual_num_users > 1 else 0)
            num_connections = random.randint(0, max_conn_this_user)

            possible_connections = [u for u in range(1, actual_num_users + 1) if u != i]

            if not possible_connections:
                connections = []
            else:
                num_connections = min(num_connections, len(possible_connections))
                connections = random.sample(possible_connections, num_connections)

            if connections:
                f.write(",".join(map(str, connections)) + "\n")
            else:
                f.write("\n")
            count += 1
            if actual_num_users > 10000 and count % (actual_num_users // 100) == 0:
                if __name__ == "__main__":
                    progress = (count / actual_num_users) * 100
                    sys.stdout.write(f"\rGenerated user connection data: {progress:.2f}% complete ({count}/{actual_num_users})")
                    sys.stdout.flush()

    if actual_num_users > 10000 and __name__ == "__main__":
        sys.stdout.write("\n")
    if __name__ == "__main__":
        print(f"Finished generating {filename} with {count} users.")

# NUM_USERS (variable global) se establece arriba.
# main.py puede importar NUM_USERS de este módulo para saber con cuántos usuarios se generaron los datos
# si data_generator.py se ejecutó como script principal antes.
# Si main.py llama a las funciones generate_*, esas funciones usarán el NUM_USERS global
# a menos que se les pase num_users_to_generate.

if __name__ == "__main__":
    print(f"--- Data Generation Script (Executing Directly) ---")
    # NUM_USERS ya está configurado por la lógica al inicio del script (CMD arg o default).
    print(f"Target number of users for this run: {NUM_USERS}")

    # Las funciones usarán el NUM_USERS global porque num_users_to_generate no se pasa.
    generate_location_data()
    generate_user_data()

    print(f"\nSuccessfully generated simulated data for {NUM_USERS} users.")
    print(f"Files: simulated_locations.txt, simulated_users.txt")
    print(f"To use a different number of users, run: python {sys.argv[0]} <number_of_users>")
