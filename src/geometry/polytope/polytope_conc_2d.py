from abc import ABC, abstractmethod
import numpy as np
from typing import Optional
from geometry import AbstractPoint, AbstractHalfspace, Hyperplane
from common import Edge
from .polytope import Polytope
import polytope as pc
from scipy.spatial import ConvexHull
import itertools

class ConcretePolytope2D(Polytope):
  # Implementación de politopos 2D (hoja del Composite)

  _ambDim: int # dimensión ambiental
  _boundaries: list['Polytope']
  _vertices: np.ndarray
  _A: np.ndarray 
  _b: np.ndarray
  _supporting_hyperplane: Hyperplane
  _halfspaces: list[AbstractHalfspace]

  def __init__(self, 
               intDim: int,
               ambDim: int,
               vertices: Optional['tuple[AbstractPoint, ...]'] = None, 
               A: Optional['np.ndarray'] = None, 
               b: Optional['np.ndarray'] = None):
    self._intDim = 2
    self._ambDim = ambDim
    if A is not None and b is not None and vertices is None:
      self._A = A
      self._b = b
      self._set_vertices_from_hrep()
    elif A is None and b is None and vertices is not None and len(vertices) > 2:
      pointsArray = np.array([list(v.get_point()) for v in vertices])
      self._vertices = pointsArray  
      self._set_h_rep_from_vertices()
    else:
      raise ValueError("Inicialización inválida: Proveer vértices o (A, b)")

  def _set_vertices_from_hrep(self):
    # calcula los vértices si se inicializó con h-rep
    poly = pc.Polytope(self._A, self._b)
    self._vertices = pc.extreme(poly)

  def _set_h_rep_from_vertices(self):
    # calcula A y b si se inicializó con vértices
    poly = pc.qhull(self._vertices)
    poly = pc.reduce(poly)
    self._A, self._b = poly.A, poly.b

  def get_vertices(self) -> np.ndarray:
    if self._vertices is not None:
      return self._vertices

  def get_hrep(self) -> tuple[np.ndarray, np.ndarray]:
    # permite obtener las matrices A y b que definen al politopo (Ax <= b)
    if self._A is not None and self._b is not None:
      return self._A, self._b

  def get_edges(self) -> list[tuple[tuple[float, ...], tuple[float, ...]]]:
    # retorna las aristas del politopo
    if self._vertices is None:
      return [] 
        
    hull = ConvexHull(self._vertices)
    unique_edges = set()
    
    for simplex in hull.simplices:
      # itertools.combinations saca todos los pares posibles del simplex
      # En 2D saca 1 par. En 3D saca 3 pares (los 3 lados del triángulo).
      for i, j in itertools.combinations(simplex, 2):
        # Ordenamos los índices para que (v1, v2) y (v2, v1) colapsen en el set
        idx_min, idx_max = min(i, j), max(i, j)
        p1 = tuple(self._vertices[idx_min])
        p2 = tuple(self._vertices[idx_max])
        unique_edges.add((p1, p2))   
            
    return list(unique_edges)

  def get_boundaries(self):
    return

  def get_halfspaces(self) -> list[AbstractHalfspace]:
    # devuelve la lista de los semiespacios que definen al politopo
    if self._halfspaces is None:
      A, b = self._A, self._b
      self._halfspaces = []
      for i in range(len(b)):
        A_face = A[i]
        b_face = b[i]
        hs = AbstractHalfspace(A_face, b_face)
        self._halfspaces.append(hs)
    return self._halfspaces

  def get_supporting_hyperplane(self) -> Hyperplane:
    # retorna el hiperplano que contiene al politopo si intDim < ambDim
    if self._intDim == self._ambDim:
      return
    points = []
    for i in range(self._intDim):
      points[i] = self._vertices[i]
    return Hyperplane(points)

  def reduce(self):
    # elimina las inecuaciones redundantes
    pass