import numpy as np
import polytope as pc
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.spatial import ConvexHull
from sci import SCIChecker
from geometry import GeometryFactory
from coverage_checker import PredicatesFactory
from affine_system import SwitchedAffineSystem
from common import PolytopeMap


def plot_filled_scenario(title: str, original_poly: pc.Polytope, checker: 'SCIChecker', coverage_result: bool, subregions_map: PolytopeMap):
    """Grafica el politopo y las subregiones con relleno traslúcido."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 1. Dibujamos la caja original S como referencia (fondo gris)
    original_poly.plot(ax, color='lightgray', alpha=0.3, edgecolor='black', linewidth=2)
    
    # Colores base para imitar la paleta de MATLAB
    colors = ['#1f77b4', '#ff7f0e', '#d62728', '#9467bd', '#2ca02c'] 
    
    # 3. Reconstruimos los polígonos cerrados a partir de los puntos
    for mode_idx, halfspaces_list in enumerate(subregions_map):
        if not halfspaces_list: 
            continue
            
        points = []
        for hs in halfspaces_list:
            points.append([hs.p1.x, hs.p1.y])
            points.append([hs.p2.x, hs.p2.y])
            
        points_array = np.array(points)
        
        # Usamos ConvexHull para asegurar que los puntos formen un polígono perfecto
        if len(points_array) >= 3:
            try:
                hull = ConvexHull(points_array)
                # Creamos el parche relleno
                poly_patch = patches.Polygon(
                    points_array[hull.vertices], 
                    closed=True,
                    facecolor=colors[mode_idx % len(colors)],
                    edgecolor=colors[mode_idx % len(colors)],
                    alpha=0.6, # Transparencia para ver superposiciones
                    linewidth=1.5,
                    label=f'Modo {mode_idx}'
                )
                ax.add_patch(poly_patch)
            except Exception as e:
                print(f"No se pudo rellenar el Modo {mode_idx}: {e}")

    # Configuraciones estéticas
    ax.set_title(f"{title}\nResultado de Cobertura: {coverage_result}", fontsize=14)
    ax.set_xlim([-1.5, 1.5]) # Ajustado al marco de tus imágenes
    ax.set_ylim([-1.5, 1.5])
    ax.grid(True, linestyle='--', alpha=0.5)
    
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        # Evitar leyendas duplicadas si el parche base de pc.Polytope metió basura
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper right')
        
    plt.show()

def run_matlab_validation():
    # Setup de dependencias compartidas
    geometry_2d = GeometryFactory[2]()
    predicates_2d = PredicatesFactory[2]() 
    
    # --- 3. Conjunto Objetivo S (Caja [-1, 1] x [-1, 1]) ---
    A_poly = np.array([[ 1.0,  0.0], 
                       [-1.0,  0.0], 
                       [ 0.0,  1.0], 
                       [ 0.0, -1.0]])
    b_poly = np.array([[1.0], [1.0], [1.0], [1.0]]) 
    base_polytope = pc.Polytope(A_poly, b_poly)

    # --- 2. Definición del Sistema Afín Conmutado ---
    rho = 10.15
    A_base = np.array([[1.0, -rho], 
                       [rho,  1.0]])
    k1 = 0.2
    A_1 = k1 * A_base
    
    # Traducimos las celdas A{i} y b{i} de MATLAB al diccionario
    # Notar que usamos multiplicación matricial (@) para los cálculos de b
    modes_dict = {
        0: (A_1,    -A_1 @ np.array([[-4.0], [ 0.0]])),
        1: (A_1,    -A_1 @ np.array([[ 0.0], [-4.0]])),
        2: (A_1,    -A_1 @ np.array([[ 4.0], [ 0.0]])),
        3: (A_1,    -A_1 @ np.array([[ 0.0], [ 4.0]])),
        4: (A_base,        np.array([[ 0.0], [ 0.0]]))
    }
    
    sas = SwitchedAffineSystem(modes_dict)
    
    # Dwell time global del problema
    dwell_time = 0.2 

    # =================================================================
    # Experimento 1: K = 3 (Debería dejar huecos)
    # =================================================================
    print("Ejecutando Experimento K=3 (h ≈ 0.067)...")
    checker_k3 = SCIChecker(geometry=geometry_2d, 
                                    predicates=predicates_2d, 
                                    polytope=base_polytope, 
                                    sas=sas)
    
    result_k3, sub_k3 = checker_k3.sci_check(dwellTime=dwell_time, K=3)
    plot_filled_scenario("K = 3 (h = 0.067)", base_polytope, checker_k3, result_k3, sub_k3)

    # =================================================================
    # Experimento 2: K = 12 (NO debería cubrir)
    # =================================================================
    print("\nEjecutando Experimento K=12 (h ≈ 0.017)...")
    checker_k12 = SCIChecker(geometry=geometry_2d, 
                                        predicates=predicates_2d, 
                                        polytope=base_polytope, 
                                        sas=sas)
    
    result_k12, sub_k12 = checker_k12.sci_check(dwellTime=dwell_time, K=12)
    plot_filled_scenario("K = 12 (h = 0.017)", base_polytope, checker_k12, result_k12, sub_k12)

    # =================================================================
    # Experimento 3: K = 350 (Debería cubrir?)
    # =================================================================
    print("\nEjecutando Experimento K=350 (h ≈ )...")
    checker_k350 = SCIChecker(geometry=geometry_2d, 
                                        predicates=predicates_2d, 
                                        polytope=base_polytope, 
                                        sas=sas)
        
    result_k350, sub_k350 = checker_k350.sci_check(dwellTime=dwell_time, K=350)
    plot_filled_scenario("K = 350 (h = )", base_polytope, checker_k350, result_k350, sub_k350)

if __name__ == "__main__":
    run_matlab_validation()