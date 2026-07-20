import sys
import os

# 1. Calculamos la ruta absoluta a la carpeta raíz del proyecto (subiendo un nivel '..')
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 2. Inyectamos esa ruta en el radar de búsqueda de Python
sys.path.insert(0, ruta_raiz)

import polytope as pc
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from scipy.spatial import ConvexHull

from geometry.geometry_2d import Geometry2d
from coverage_checker.predicates.predicates_2d import Predicates2d
from sci import SCIChecker

# --- DEFINICIÓN GEOMÉTRICA ---

# A. Politopo central (Cuadrado negro) de (2,2) a (8,8)
# Lo definimos fácil con los límites X e Y
P = pc.box2poly([[2.0, 8.0], [2.0, 8.0]])

# B. Subregiones (Ligeramente rotadas para simular tu imagen)
# S1: Izquierda (Verde) - Cubre los vértices (2,2) y (2,8)
S1_verts = np.array([[1.0, 0.5], [3.0, 0.5], [3.5, 9.5], [1.5, 9.5]])
S1 = pc.qhull(S1_verts)

# S2: Arriba (Verde) - Cubre los vértices (2,8) y (8,8)
S2_verts = np.array([[0.5, 7.5], [9.5, 7.0], [9.5, 9.0], [0.5, 9.5]])
S2 = pc.qhull(S2_verts)

# S3: Derecha (Verde) - Cubre los vértices (8,8) y (8,2)
S3_verts = np.array([[7.0, 0.5], [9.5, 0.5], [9.0, 9.5], [6.5, 9.5]])
S3 = pc.qhull(S3_verts)

# S4: Abajo (Rojo) - Cubre la arista inferior y colabora en los vértices
S4_verts = np.array([[0.5, 1.0], [9.5, 0.5], [9.5, 2.5], [0.5, 3.0]])
S4 = pc.qhull(S4_verts)

# S5: Centro (Azul/Violeta) - Cubre el hueco interior y la diagonal de triangulación
# Sentido Antihorario (CCW) garantizado
S5_verts = np.array([[3.0, 2.5], [7.0, 2.5], [7.0, 7.5], [3.0, 7.5]])
S5 = pc.qhull(S5_verts)

# S5: Diagonal Ascendente (Cubre de 2,2 a 8,8) - Sentido Antihorario
S6_verts = np.array([
    [2.5, 3.5],  # Abajo-Izquierda (Arriba de la diagonal)
    [3.5, 2.5],  # Abajo-Izquierda (Abajo de la diagonal)
    [7.5, 6.5],  # Arriba-Derecha (Abajo de la diagonal)
    [6.5, 7.5]   # Arriba-Derecha (Arriba de la diagonal)
])
S6 = pc.qhull(S6_verts)

# S6: Diagonal Descendente (Cubre de 2,8 a 8,2) - Sentido Antihorario
S7_verts = np.array([
    [2.5, 6.5],  # Arriba-Izquierda (Abajo de la diagonal)
    [6.5, 2.5],  # Abajo-Derecha (Abajo de la diagonal)
    [7.5, 3.5],  # Abajo-Derecha (Arriba de la diagonal)
    [3.5, 7.5]   # Arriba-Izquierda (Arriba de la diagonal)
])
S7 = pc.qhull(S7_verts)

def extraer_semiespacios(poly: pc.Polytope, fabrica: Geometry2d):
    """Extrae los vértices del politopo, los ordena y crea Halfspace2D exactos."""
    caras = []
    
    # poly.V devuelve las coordenadas crudas de los vértices
    vertices = pc.extreme(poly)
    
    # ConvexHull encuentra el perímetro y ordena los vértices en sentido antihorario (CCW)
    hull = ConvexHull(vertices)
    indices_ordenados = hull.vertices 
    cantidad_vertices = len(indices_ordenados)
    
    for i in range(cantidad_vertices):
        # Tomamos el vértice actual y el siguiente (con módulo para cerrar el ciclo)
        idx_actual = indices_ordenados[i]
        idx_siguiente = indices_ordenados[(i + 1) % cantidad_vertices]
        
        v_actual = vertices[idx_actual]
        v_siguiente = vertices[idx_siguiente]
        
        # Creamos los objetos Point2D usando tu fábrica
        # Usamos los mismos índices del hull como ID para mantener un rastro
        p1 = fabrica.create_point((float(v_actual[0]), float(v_actual[1])))
        p2 = fabrica.create_point((float(v_siguiente[0]), float(v_siguiente[1])))
        
        # Creamos el semiespacio a partir de los dos puntos
        cara = fabrica.create_halfspace((p1, p2))
        caras.append(cara)
        
    return caras

# --- FUNCIÓN AUXILIAR PARA GRAFICAR ---
def plot_escenario(ax, polytope, subregions, titulo, resultado_test):
    # Dibujamos el politopo negro central
    # Como sabemos que es un cuadrado [2,8]x[2,8], hardcodeamos los vértices para simplificar
    poly_verts = np.array([[2, 2], [8, 2], [8, 8], [2, 8]])
    p_patch = patches.Polygon(poly_verts, closed=True, fill=False, edgecolor='black', linewidth=2, zorder=5)
    ax.add_patch(p_patch)

    # Diccionario de colores para mantener la consistencia con tu imagen
    colores = {1: 'limegreen', 2: 'limegreen', 3: 'limegreen', 4: 'red', 5: 'blueviolet', 6: 'pink', 7: 'yellow'}

    # Dibujamos cada subregión
    for sid, subreg in subregions.items():
        # Extraemos vértices del polytope
        v = pc.extreme(subreg)
        if len(v) > 0:
            # Usamos ConvexHull para ordenar los vértices y que matplotlib dibuje bien el polígono
            hull = ConvexHull(v)
            v_ordenados = v[hull.vertices]
            color = colores.get(sid, 'blue')
            patch = patches.Polygon(v_ordenados, closed=True, fill=False, edgecolor=color, linewidth=2)
            ax.add_patch(patch)

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.set_title(f"{titulo}\nResultado SCIChecker: {resultado_test}")
    ax.grid(True, linestyle=':', alpha=0.6)

# --- EJECUCIÓN DE LOS TESTS ---
def main():
    geom = Geometry2d()
    preds = Predicates2d()

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle("Pruebas de Cobertura - SCIChecker", fontsize=16, fontweight='bold')

    # ---------------------------------------------------------
    # CASO 1: Éxito Total (Como en la imagen)
    # ---------------------------------------------------------
    # Todas las subregiones presentes. Vértices y aristas cubiertos.
    subs_c1_poly = {1: S1, 2: S2, 3: S3, 4: S4, 5: S5}
    subs_c1 = [extraer_semiespacios(S1, geom), extraer_semiespacios(S2, geom),
               extraer_semiespacios(S3, geom), extraer_semiespacios(S4, geom), 
               extraer_semiespacios(S5, geom)]
    
    # IMPORTANTE: Metelo en un try/except por si el algoritmo lanza excepción al fallar
    checker_c1 = SCIChecker(geom, preds, P, subs_c1)
    res_c1 = checker_c1.sci_check() 
    plot_escenario(axes[0], P, subs_c1_poly, "Caso 1: Cobertura Completa", res_c1)

    # ---------------------------------------------------------
    # CASO 2: Falla la cobertura de la arista inferior (C2)
    # ---------------------------------------------------------
    # Quitamos el rectángulo rojo (ID 4). 
    # Los vértices de abajo siguen estando cubiertos por S1 y S3, pero la arista queda expuesta al medio.
    subs_c2_poly = {1: S1, 2: S2, 3: S3, 5: S5}
    subs_c2 = [extraer_semiespacios(S1, geom), extraer_semiespacios(S2, geom),
               extraer_semiespacios(S3, geom)]

    checker_c2 = SCIChecker(geom, preds, P, subs_c2)
    
    try:
        res_c2 = checker_c2.sci_check()
    except Exception as e:
        res_c2 = f"FALLÓ (Como se esperaba)"
    
    plot_escenario(axes[1], P, subs_c2_poly, "Caso 2: Arista Expuesta", res_c2)

    # ---------------------------------------------------------
    # CASO 3: Falla la cobertura de un vértice (C1)
    # ---------------------------------------------------------
    # Quitamos el rectángulo rojo (ID 4) y el verde derecho (ID 3).
    # El vértice inferior derecho (8,2) queda completamente al descubierto.
    '''subs_c3_poly = {1: S1, 2: S2}
    subs_c3 = [extraer_semiespacios(S1, geom), extraer_semiespacios(S2, geom)]
    checker_c3 = SCIChecker(geom, preds, P, subs_c3)
    
    try:
        res_c3 = checker_c3.sci_check()
    except Exception as e:
        res_c3 = f"FALLÓ (Como se esperaba)"
        
    plot_escenario(axes[2], P, subs_c3_poly, "Caso 3: Vértice Expuesto", res_c3)'''

     # ---------------------------------------------------------
    # CASO 4: Falla la cobertura del interior (C3)
    # ---------------------------------------------------------
    subs_c4_poly = {1: S1, 2: S2, 3: S3, 4: S4, 6: S6, 7: S7}
    subs_c4 = [extraer_semiespacios(S1, geom), extraer_semiespacios(S2, geom),
               extraer_semiespacios(S3, geom), extraer_semiespacios(S4, geom), 
               extraer_semiespacios(S6, geom), extraer_semiespacios(S7, geom)]
    checker_c4 = SCIChecker(geom, preds, P, subs_c4)
    
    try:
        res_c4 = checker_c4.sci_check()
    except Exception as e:
        res_c4 = f"FALLÓ (Como se esperaba)"
        
    plot_escenario(axes[2], P, subs_c4_poly, "Caso 3: Interior no cubierto", res_c4)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()