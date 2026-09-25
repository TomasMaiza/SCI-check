import numpy as np
from .geometry import AbstractGeometry, Halfspace
from .structs_3d import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from .polytope import Polytope
  from src.common.types import Edge

class Geometry3d(AbstractGeometry):
  # geometría 3d
  def create_point(self, coord: tuple[float, ...]) -> Point3D: # crea un punto
    return Point3D(x = coord[0], y = coord[1], z = coord[2])

  def create_simplex(self, vertices: tuple[Point3D, ...]) -> Tetrahedron3D:
    return Tetrahedron3D(vertices)

  def create_halfspace(self, points: tuple[Point3D, Point3D]) -> Halfspace: 
    # crea un semiespacio
    return Halfspace(points = list(points))

  def create_halfspace_from_vector(self, normalVector: np.ndarray, b: float) -> Halfspace: # crea un semiespacio
    return Halfspace(normalVector = normalVector, b = b)

  def get_dimension(self) -> int: # retorna la dimensión
    return 3

  def create_halfspaces_list(self, subregionPolytope: 'Polytope') -> list[Halfspace]:
    return subregionPolytope.get_halfspaces()

  def get_polytope_edges(self, polytope: 'Polytope') -> list['Edge']:
    # devuelve una lista de las aristas de un politopo como una lista de (Point2D, Point2D)
    edges = polytope.get_edges()
    geomEdges = []
    for e in edges:
      v1, v2 = Point3D(x = e[0][0], y = e[0][1], z = e[0][2]), Point3D(x = e[1][0], y = e[1][1], z = e[1][2])
      geomEdges.append((v1, v2))
    return geomEdges