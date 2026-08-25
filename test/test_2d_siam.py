import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.spatial import ConvexHull
from sci import SCIChecker
from coverage_checker import *
from geometry import GeometryFactory, Polytope, PolytopeImp
from coverage_checker import PredicatesFactory
from affine_system import SwitchedAffineSystem
from common import PolytopeMap, setup_logger

def set_sci(polytope: PolytopeImp, sas: SwitchedAffineSystem):
  checker = SCIChecker(GeometryFactory[2](), PredicatesFactory[2](), CoverageCheckerFactory[2], polytope, sas)
  return checker

def politopo():
  geom = GeometryFactory[2]()
  v = (geom.create_point(coord = (np.sqrt(2), 0)), 
       geom.create_point(coord = (-np.sqrt(2), 0)),
       geom.create_point(coord = (0, np.sqrt(2))),
       geom.create_point(coord = (0, -np.sqrt(2))))
  polytope = PolytopeImp(vertices = v)
  return polytope

def sistema():
  rho = 0.5
  modos = {}
  modos[1] = (np.array([[rho, 0], [1, rho]]), np.array([0, -10]).reshape(-1, 1))
  modos[2] = (np.array([[rho, 0], [1, rho]]), np.array([-10, 0]).reshape(-1, 1))
  modos[3] = (np.array([[rho, 1], [0, rho]]), np.array([0, 10]).reshape(-1, 1))
  modos[4] = (np.array([[rho, 1], [0, rho]]), np.array([10, 0]).reshape(-1, 1))
  sas = SwitchedAffineSystem(modos)
  return sas

def ejecutar_test(T: float, K: int):
  poly = politopo()
  sas = sistema()
  checker = set_sci(poly, sas)
  cov, subregions = checker.sci_check(T, K)
  print(f"El resultado es: {cov}")
  plot_filled_scenario("Test 2D SIAM", poly, cov, subregions)

def plot_filled_scenario(title: str, original_poly: Polytope, coverage_result: bool, subregions_map: PolytopeMap):
    """Grafica el politopo y las subregiones con relleno traslúcido."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 1. Dibujamos la caja original S como referencia (fondo gris)
    original_poly.polytope.plot(ax, color='lightgray', alpha=0.3, edgecolor='black', linewidth=2)
    
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

if __name__ == "__main__":
  setup_logger()
  ejecutar_test(T = 0.1, K = 12)