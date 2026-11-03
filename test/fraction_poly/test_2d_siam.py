import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.spatial import ConvexHull
from sci import SCIChecker
from coverage_checker import *
from geometry import Polytope, FractionPolytope2D
from coverage_checker import PredicatesFactory
from affine_system import SwitchedAffineSystem
import polytope as pc
from common import setup_logger, Point

def set_sci(polytope: FractionPolytope2D, sas: SwitchedAffineSystem):
  checker = SCIChecker(2, polytope, sas)
  return checker

def politopo():
  v = ((np.sqrt(2), 0), 
       (-np.sqrt(2), 0),
       (0, np.sqrt(2)),
       (0, -np.sqrt(2)))
  polytope = FractionPolytope2D(intDim = 2, ambDim = 2, vertices = v)
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

def plot_filled_scenario(title: str, original_poly: Polytope, coverage_result: bool, subregions_map: list[Polytope]):
    """Grafica el politopo y las subregiones con relleno traslúcido."""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 1. Dibujamos la caja original S como referencia (fondo gris)
    poly = pc.qhull(original_poly.get_vertices())
    poly.plot(ax, color='lightgray', alpha=0.3, edgecolor='black', linewidth=2)
    
    # Colores base para imitar la paleta de MATLAB
    colors = ['#1f77b4', '#ff7f0e', '#d62728', '#9467bd', '#2ca02c'] 
    
    # 3. Reconstruimos los polígonos cerrados a partir de los puntos
    for mode_idx, p in enumerate(subregions_map):
        subrPoly = pc.qhull(vertices = p.get_vertices())
        subrPoly.plot(ax, color=colors[mode_idx], alpha=0.3, edgecolor='black', linewidth=2)

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
  ejecutar_test(T = 0.1, K = 1)