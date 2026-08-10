import numpy as np
import numpy.typing as npt
from scipy.spatial import ConvexHull
from .subregionsStrategy import SubregionsStrategy
from affine_system import *
from common import PolytopeMap
from geometry import AbstractHalfspace, AbstractGeometry, Polytope
from .approximations import Euler, Taylor
from affine_system import SwitchedAffineSystem, AffineMode
from .matrices import partition_matrices

class Subregions(SubregionsStrategy):
  def __init__(self, geometry: AbstractGeometry):
    self._approxMethod = Taylor
    self._geometry = geometry

  def get_polytope_vertices_CCW(self, subregionPolytope: Polytope) -> list[list[float]]:
    # Extrae y ordena los vértices del politopo en sentido antihorario (CCW).
    vertices = subregionPolytope.get_vertices() # obtengo los vértices del politopo
    if vertices is None or len(vertices) < 3:
        return vertices.tolist() if vertices is not None else []
    hull = ConvexHull(vertices) # ordenamos los vértices en sentido antihorario con ConvexHull
    sortedVertices = vertices[hull.vertices]
    return sortedVertices.tolist()
    

  def _create_halfspaces_list(self, subregionPolytope: Polytope) -> list[AbstractHalfspace]:
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
                    polytope: Polytope, 
                    K: int, 
                    h: float) -> list[AbstractHalfspace]:
    # obtiene la subregión para un modo particular
    approx = self._approxMethod(subsystem, polytope, scaling=1, order=4)
    r = 0 # r_0
    errorSeq = approx.error_sequence(h, K)
    phi = approx.get_matrix(h) # matriz de la aproximación
    dim = phi.shape[0]
    phi_k = np.eye(dim, dtype=np.float64) # matriz de la aproximación para el paso k
    subregionH = [] # apilamos las matrices de las inecuaciones
    subregionc = []
    for k in range(0, K + 1):
      r = errorSeq[k]
      midr = approx.error_bound(r, h/2)
      Hplus, Hminus, c = partition_matrices(polytope, subsystem, r, h, midr)
      if k > 0:
        subregionH.append(Hminus @ phi_k)
        subregionc.append(c)
      if k < K:
        subregionH.append(Hplus @ phi_k)
        subregionc.append(c)
      # r = approx.error_bound(r, abs(h)) # r para el próximo paso
      phi_k = phi @ phi_k
    matrixH = np.vstack(subregionH)
    matrixc = np.vstack(subregionc)
    # obtengo A y b separando la última columna de matrixH y me queda que Ax <= c - b
    matrixA, matrixb = np.hsplit(matrixH, [dim - 1]) # obtiene A y b separando la últ col de H
    matrixb = matrixc - matrixb
    subregionPolytope = type(polytope)(A = matrixA, b = matrixb)
    subregionPolytope.reduce()
    return self._create_halfspaces_list(subregionPolytope)

  def get_subregions(self, 
                     sas: SwitchedAffineSystem, 
                     polytope: Polytope, 
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

