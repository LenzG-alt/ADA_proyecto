import matplotlib.pyplot as plt
import os

def graficar_ubicaciones(ubicaciones):
    os.makedirs("resultados/graficos", exist_ok=True)
    lats, lons = zip(*ubicaciones)
    
    plt.figure(figsize=(10, 6))
    plt.scatter(lons, lats, s=0.5, alpha=0.5, color='blue')
    plt.title("Distribución Geográfica de Usuarios")
    plt.xlabel("Longitud")
    plt.ylabel("Latitud")
    plt.grid(True)
    plt.savefig("resultados/graficos/distribucion_geografica.png")
    plt.show()