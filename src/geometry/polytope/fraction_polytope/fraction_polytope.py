import numpy as np
from typing import Optional, TYPE_CHECKING
from geometry import Halfspace, Hyperplane
from polytope import Polytope
from .fraction_polytope_2d import FractionPolytope2D
from .julia_adapter import *
from common import Point, Edge

class FractionPolytope(Polytope):
  # Implementación de politopos

  _intDim: int # dimensión intrínseca del politopo
  _ambDim: int # dimensión ambiental
  _boundaries: list['Polytope']
  _vertices: np.ndarray
  _A: np.ndarray 
  _b: np.ndarray
  _supporting_hyperplane: Hyperplane
  _halfspaces: list[Halfspace]
  _centroid: 'Point'

  def __init__(self, 
               intDim: int,
               ambDim: int,
               vertices: Optional['list[Point]'] = None,
               verticesnp: Optional['np.ndarray'] = None,
               A: Optional['np.ndarray'] = None, 
               b: Optional['np.ndarray'] = None,
               jlPoly = None):

    if (A is None or b is None) and vertices is None and verticesnp is None and jlPoly is None:
      raise ValueError("Inicialización inválida: Proveer vértices o (A, b)")

    self._intDim = intDim
    self._ambDim = ambDim
    self._halfspaces = None
    self._centroid = None
    self._A = A
    self._b = b

    if verticesnp is not None:
      self._vertices = verticesnp
    elif vertices is not None:
      self._vertices = np.array(vertices) 
    else:
      self._vertices = None

    if jlPoly is not None:
      self._jlPoly = jlPoly
    else:
      self._jlPoly = create_polytope(self._vertices, A, b)

  def get_vertices(self) -> np.ndarray:
    if self._vertices is None:
      self._vertices = get_poly_vertices(self._jlPoly)
    return self._vertices

  def get_hrep(self) -> tuple[np.ndarray, np.ndarray]:
    # permite obtener las matrices A y b que definen al politopo (Ax <= b)
    if self._A is None or self._b is None:
      self._A, self._b = get_poly_hrep(self._jlPoly)
    return self._A, self._b

  def get_hrep_normalized(self) -> tuple[np.ndarray, np.ndarray]:
    # permite obtener las matrices A y b que definen al politopo (Ax <= b) normalizadas
    return get_poly_hrep_normalized(self._jlPoly)

  def get_edges(self) -> list['Edge']:
    # retorna las aristas del politopo
    pass

  def get_boundaries(self):
    if hasattr(self, '_boundaries') and self._boundaries:
      return self._boundaries

    self._boundaries = []

    jlFacets = get_poly_facets(self._jlPoly)

    for facet in jlFacets:
      if self._intDim == 3:
        boundary = FractionPolytope2D(intDim=2,
                                      ambDim = self._ambDim,
                                      jlPoly=facet)
      else:
        boundary = FractionPolytope(intDim=self._intDim - 1,
                                    ambDim=self._ambDim,
                                    jlPoly = facet)  
      self._boundaries.append(boundary)

    return self._boundaries

  def get_halfspaces(self) -> list[Halfspace]:
    if self._halfspaces is None:
      self._halfspaces = []
      A, b = self.get_hrep()
      boundaries = self.get_boundaries()
      for i in range(len(b)):
        normal = A[i]
        offset = b[i]
        faceVertices = boundaries[i].get_vertices()
        facePoints = [tuple(float(coord) for coord in vertex) for vertex in faceVertices]
        hs = Halfspace(points=facePoints, normalVector=normal, b=offset)
        self._halfspaces.append(hs)
    return self._halfspaces

  def get_supporting_hyperplane(self) -> Hyperplane:
    # retorna el hiperplano que contiene al politopo si intDim < ambDim
    pass

  def reduce(self):
    # elimina las inecuaciones redundantes
    pass

  def get_centroid(self) -> 'Point':
    # retorna el centroide del politopo
    if self._centroid is None:
      self._centroid = get_poly_centroid(self._jlPoly)
    return self._centroid
