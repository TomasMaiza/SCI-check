import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import scipy
print(scipy.__file__)

# 1. Definimos una nube de puntos desordenados.
# Hay 4 puntos que forman un cuadrado exterior y 3 puntos que caen adentro.
puntos = np.array([
    [2, 2], [4, 0], [0, 4], [1, 3], 
    [0, 0], [3, 1], [4, 4]
])

# 2. Scipy hace la magia llamando a Qhull en C
hull = ConvexHull(puntos)

# 3. hull.vertices tiene el "array mágico" con los índices ordenados en CCW
indices_ccw = hull.vertices

print("--- RESULTADOS DEL CONVEX HULL ---")
print(f"Índices originales ordenados: {indices_ccw}")

# 4. Usamos esos índices para filtrar y ordenar el arreglo original
vertices_ordenados = puntos[indices_ccw]

print("\nCoordenadas resultantes (recorriendo el perímetro CCW):")
for idx in indices_ccw:
    print(f"Índice {idx} -> {puntos[idx]}")

# 5. (Opcional) Lo ploteamos para ver el recorrido con nuestros propios ojos
plt.figure(figsize=(6, 6))
plt.plot(puntos[:,0], puntos[:,1], 'o', label='Puntos originales')

# Dibujamos las aristas uniendo los vértices ordenados 
# (agregamos el primer punto al final para cerrar el dibujo)
puntos_cerrados = np.vstack((vertices_ordenados, vertices_ordenados[0]))
plt.plot(puntos_cerrados[:,0], puntos_cerrados[:,1], 'r-', lw=2, label='Envolvente CCW')

# Le ponemos el índice al lado a cada punto para ver el orden
for i, coord in enumerate(puntos):
    plt.text(coord[0] + 0.1, coord[1], str(i), fontsize=12, color='blue')

plt.title("Ordenamiento del Convex Hull")
plt.legend()
plt.grid(True, linestyle=':')
plt.show()