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
from coverage_checker.predicates_2d import Predicates2d
from sci import SCIChecker 
from common.types import PolytopeMap

# --- DEFINICIÓN GEOMÉTRICA ---

# A. Politopo central (Cuadrado negro) de (2,2) a (8,8)
# Lo definimos fácil con los límites X e Y
P = pc.box2d([2, 8], [2, 8])

# B. Subregiones (Ligeramente rotadas para simular tu imagen)
# S1: Izquierda (Verde) - Cubre los vértices (2,2) y (2,8)
S1_verts = np.array([[1.0, 0.5], [3.0, 0.5], [3.5, 9.5], [1.5, 9.5]])
S1 = pc.qhull(S1_verts)

# S2: Arriba (Verde) - Cubre los vértices (2,8) y (8,8)
S2_verts = np.array([[0.5, 7.5], [0.5, 9.5], [9.5, 9.0], [9.5, 7.0]])
S2 = pc.qhull(S2_verts)

# S3: Derecha (Verde) - Cubre los vértices (8,8) y (8,2)
S3_verts = np.array([[7.0, 0.5], [9.5, 0.5], [9.0, 9.5], [6.5, 9.5]])
S3 = pc.qhull(S3_verts)

# S4: Abajo (Rojo) - Cubre la arista inferior y colabora en los vértices
S4_verts = np.array([[0.5, 1.0], [0.5, 3.0], [9.5, 2.5], [9.5, 0.5]])
S4 = pc.qhull(S4_verts)

# --- FUNCIÓN AUXILIAR PARA GRAFICAR ---
def plot_escenario(ax, polytope, subregions, titulo, resultado_test):
    # Dibujamos el politopo negro central
    # Como sabemos que es un cuadrado [2,8]x[2,8], hardcodeamos los vértices para simplificar
    poly_verts = np.array([[2, 2], [8, 2], [8, 8], [2, 8]])
    p_patch = patches.Polygon(poly_verts, closed=True, fill=False, edgecolor='black', linewidth=2, zorder=5)
    ax.add_patch(p_patch)

    # Diccionario de colores para mantener la consistencia con tu imagen
    colores = {1: 'limegreen', 2: 'limegreen', 3: 'limegreen', 4: 'red'}

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
    subs_c1 = {1: S1, 2: S2, 3: S3, 4: S4} # Pasalo por tu PolytopeMap si es necesario
    
    # IMPORTANTE: Metelo en un try/except por si el algoritmo lanza excepción al fallar
    checker_c1 = SCIChecker(geom, preds, P, subs_c1)
    res_c1 = checker_c1.sci_check() 
    plot_escenario(axes[0], P, subs_c1, "Caso 1: Cobertura Completa", res_c1)

    # ---------------------------------------------------------
    # CASO 2: Falla la cobertura de la arista inferior (C2)
    # ---------------------------------------------------------
    # Quitamos el rectángulo rojo (ID 4). 
    # Los vértices de abajo siguen estando cubiertos por S1 y S3, pero la arista queda expuesta al medio.
    subs_c2 = {1: S1, 2: S2, 3: S3}
    checker_c2 = SCIChecker(geom, preds, P, subs_c2)
    
    try:
        res_c2 = checker_c2.sci_check()
    except Exception as e:
        res_c2 = f"FALLÓ (Como se esperaba)"
    
    plot_escenario(axes[1], P, subs_c2, "Caso 2: Arista Expuesta", res_c2)

    # ---------------------------------------------------------
    # CASO 3: Falla la cobertura de un vértice (C1)
    # ---------------------------------------------------------
    # Quitamos el rectángulo rojo (ID 4) y el verde derecho (ID 3).
    # El vértice inferior derecho (8,2) queda completamente al descubierto.
    subs_c3 = {1: S1, 2: S2}
    checker_c3 = SCIChecker(geom, preds, P, subs_c3)
    
    try:
        res_c3 = checker_c3.sci_check()
    except Exception as e:
        res_c3 = f"FALLÓ (Como se esperaba)"
        
    plot_escenario(axes[2], P, subs_c3, "Caso 3: Vértice Expuesto", res_c3)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()