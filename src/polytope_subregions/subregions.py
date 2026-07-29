import numpy as np
import numpy.typing as npt
import polytope as pc
from scipy.spatial import ConvexHull
from .subregionsStrategy import SubregionsStrategy
from affine_system import *
from common import PolytopeMap
from geometry import AbstractHalfspace, AbstractGeometry
from .approximations import Euler
from affine_system import SwitchedAffineSystem, AffineMode
from .matrices import partition_matrices

class Subregions(SubregionsStrategy):
  def __init__(self, geometry: AbstractGeometry):
    self._approxMethod = Euler
    self._geometry = geometry

  def get_polytope_vertices_CCW(self, subregionPolytope: pc.Polytope) -> list[list[float]]:
    # Extrae y ordena los vértices del politopo en sentido antihorario (CCW).
    vertices = pc.extreme(subregionPolytope) # obtengo los vértices del politopo
    if vertices is None or len(vertices) < 3:
        return vertices.tolist() if vertices is not None else []
    hull = ConvexHull(vertices) # ordenamos los vértices en sentido antihorario con ConvexHull
    sortedVertices = vertices[hull.vertices]
    return sortedVertices.tolist()
    

  def _create_halfspaces_list(self, subregionPolytope: pc.Polytope) -> list:
    sortedVertices = self.get_polytope_vertices_CCW(subregionPolytope)    
    numVertices = len(sortedVertices)
    halfspaces = []
    for i in range(numVertices): # iteramos para armar los bordes del politopo (v1, v2)
      v1 = sortedVertices[i]
      v2 = sortedVertices[(i + 1) % numVertices]
      p1 = self._geometry.create_point(v1)
      p2 = self._geometry.create_point(v2)
      hs = self._geometry.create_halfspace((p1, p2))
      halfspaces.append(hs)
    return halfspaces

  def get_subregion(self, 
                    subsystem: AffineMode, 
                    polytope: pc.Polytope, 
                    K: int, 
                    h: float) -> list[AbstractHalfspace]:
    # obtiene la subregión para un modo particular
    approx = self._approxMethod(subsystem, polytope)
    r = 0 # r_0
    phi = approx.get_matrix(h) # matriz de la aproximación
    dim = phi.shape[0]
    phi_k = np.eye(dim, dtype=np.float64) # matriz de la aproximación para el paso k
    subregionH = [] # apilamos las matrices de las inecuaciones
    subregionc = []
    for k in range(0, K + 1):
      midr = approx.error_bound(r, h/2)
      Hplus, Hminus, c = partition_matrices(polytope, subsystem, r, h, midr)
      if k > 0:
        subregionH.append(Hminus @ phi_k)
        subregionc.append(c)
      if k < K:
        subregionH.append(Hplus @ phi_k)
        subregionc.append(c)
      r = approx.error_bound(r, abs(h)) # r para el próximo paso
      phi_k = phi @ phi_k
    matrixH = np.vstack(subregionH)
    matrixc = np.vstack(subregionc)
    # cómo obtengo cada A y b?
    # Idea: obtengo A y b separando la última columna de matrixH y me queda que Ax <= c - b
    matrixA, matrixb = np.hsplit(matrixH, [dim - 1]) # obtiene A y b separando la últ col de H
    matrixb = matrixc - matrixb
    # fin
    subregionPolytope = pc.Polytope(matrixA, matrixb)
    subregionPolytope = pc.reduce(subregionPolytope)
    return self._create_halfspaces_list(subregionPolytope)

  def get_subregions(self, 
                     sas: SwitchedAffineSystem, 
                     polytope: pc.Polytope, 
                     dwellTime: float, 
                     K: int) -> PolytopeMap:
    # recibe un politopo (y todo lo necesario) para devolver la lista de subregiones
    h = dwellTime/K
    modes = sas.get_all_modes()
    polytopeMap = [] # inicializo el mapa de politopos para cada modo
    for i in modes:
      subsystem = sas.get_subsystem(i)
      halfspaces = self.get_subregion(subsystem, polytope, K, h)
      #if len(halfspaces) != 0:
      polytopeMap.append(halfspaces)
    return polytopeMap

