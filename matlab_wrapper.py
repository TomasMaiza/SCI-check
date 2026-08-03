import sys
import os

currentDir = os.path.dirname(os.path.abspath(__file__))
srcPath = os.path.join(currentDir, 'src')

if srcPath not in sys.path:
    sys.path.insert(0, srcPath)

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from sci import SCIChecker
from scipy.spatial import ConvexHull
from geometry import *
from coverage_checker import *
import polytope as pc
from affine_system import *

class MatlabWrapperSCI:
  def create_geometry_and_predicates(self, dimension: int):
    # inicializa la geometría y los predicados
    geomClass = GeometryFactory[dimension]
    predClass = PredicatesFactory[dimension]
    self._geom = geomClass()
    self._preds = predClass()
  
  def create_polytope(self, polytopeVerticesRaw: list[list[float]]):
    # se inicializa el politopo
    polytopeVertices = np.array(polytopeVerticesRaw, dtype=float) # vértices del politopo
    self._polytope = pc.qhull(polytopeVertices) # se crea el politopo

  def create_sas(self, systemRaw: list[tuple[list[list[float]], list[float]]]):
    # inicializa el sistema afín conmutado
    modesDict = {}
    for mode, (ARaw, bRaw) in enumerate(systemRaw):
      A = np.array(ARaw, dtype=np.float64)
      b = np.array(bRaw, dtype=np.float64).reshape(-1, 1)
      modesDict[mode] = (A, b)
    self._sas = SwitchedAffineSystem(modesDict)

  def plot_filled_scenario(self, title: str, original_poly: pc.Polytope, coverage_result: bool, subregions_map: list):
    # Grafica el politopo y las subregiones
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 1. Dibujamos la caja original S como referencia (fondo gris)
    try:
        original_poly.plot(ax, color='lightgray', alpha=0.3, edgecolor='black', linewidth=2)
    except Exception:
        pass # Por si la librería polytope vuelve a fallar con el original
    
    # Colores base
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

    ax.set_title(f"{title}\nResultado de Cobertura: {coverage_result}", fontsize=14)
    ax.set_xlim([-1.5, 1.5]) 
    ax.set_ylim([-1.5, 1.5])
    ax.grid(True, linestyle='--', alpha=0.5)
    
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper right')

    plt.show(block=False)
    plt.pause(0.1)

  def checking_sci(self, 
                   polytopeVerticesRaw: list[list[float]], 
                   systemRaw: list[tuple[list[list[float]], list[float]]],  # lista de tuplas (A, b)
                   dwellTime: float, 
                   K: int, 
                   dimension: int) -> bool:
    # recibe listas crudas desde MATLAB, arma la geometría y corre el SCIChecker.
    self.create_geometry_and_predicates(dimension)
    self.create_polytope(polytopeVerticesRaw)
    self.create_sas(systemRaw)
    checker = SCIChecker(self._geom, self._preds, self._polytope, self._sas)
    isSCI, subregions = checker.sci_check(dwellTime, K)
    self.plot_filled_scenario(f"K = {K}", self._polytope, isSCI, subregions)
    return isSCI