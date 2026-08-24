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
    A, b = subregionPolytope.get_hrep()
    dim = self._geometry.get_dimension()
    halfspaces = []
      
    for i in range(len(b)):
      n = A[i] # vector normal de la cara
      d = b[i] # offset de la cara
          
      idx = np.argmax(np.abs(n))
      if abs(n[idx]) < 1e-12:
        continue
              
      p0 = np.zeros(dim) # punto base en el plano
      p0[idx] = d / n[idx]
      points = [p0]
          
      for j in range(dim):
        if j != idx:
          pj = np.copy(p0)
          pj[j] += 1.0
          pj[idx] -= n[j] / n[idx]
          points.append(pj)
                  
      V = np.column_stack([p - points[0] for p in points[1:]])
      M = np.column_stack((V, n))
      if np.linalg.det(M) < 0:
        points[0], points[1] = points[1], points[0]
          
      abstractPoints = tuple(self._geometry.create_point(tuple(coords)) for coords in points)
      hs = self._geometry.create_halfspace(abstractPoints)
      halfspaces.append(hs)
          
    return halfspaces

  def get_subregion(self, 
                    subsystem: AffineMode, 
                    polytope: Polytope) -> list[AbstractHalfspace]:
    # obtiene la subregión para un modo particular
    approx = self._approxMethod(subsystem, polytope, scaling=1, order=4)
    r = 0 # r_0
    errorSeq = approx.error_sequence(self._h, self._K)
    phi = approx.get_matrix(self._h) # matriz de la aproximación
    dim = phi.shape[0]
    phi_k = np.eye(dim, dtype=np.float64) # matriz de la aproximación para el paso k
    subregionH = [] # apilamos las matrices de las inecuaciones
    subregionc = []
    for k in range(0, self._K + 1):
      r = errorSeq[k]
      midr = approx.error_bound(r, self._h/2)
      Hplus, Hminus, c = partition_matrices(polytope, subsystem, r, self._h, midr)
      if k > 0:
        subregionH.append(Hminus @ phi_k)
        subregionc.append(c)
      if k < self._K:
        subregionH.append(Hplus @ phi_k)
        subregionc.append(c)
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
    # recibe un politopo, el sistema y los parámetros para devolver la lista de subregiones
    h = dwellTime/K
    self._K = K
    self._h = h
    modes = sas.get_all_modes()
    polytopeMap = [] # inicializo el mapa de politopos para cada modo
    for i in modes:
      subsystem = sas.get_subsystem(i)
      halfspaces = self.get_subregion(subsystem, polytope)
      #if len(halfspaces) != 0:
      polytopeMap.append(halfspaces)
    return polytopeMap

