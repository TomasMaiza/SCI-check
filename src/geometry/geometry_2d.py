import numpy as np
from .geometry import AbstractGeometry
from .structs_2d import *
from scipy.spatial import ConvexHull
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from .polytope import Polytope
  from src.common.types import Edge

class Geometry2d(AbstractGeometry):
  # geometría 2d
  def create_point(self, coord: tuple[float, ...]) -> Point2D: # crea un punto
    return Point2D(x = coord[0], y = coord[1])

  def create_simplex(self, vertices: tuple[Point2D, ...]) -> Triangle2D:
    return Triangle2D(v1 = vertices[0], v2 = vertices[1], v3 = vertices[2])

  def create_halfspace(self, points: tuple[Point2D, Point2D]) -> Halfspace2D: 
    # crea un semiespacio
    return Halfspace2D(points = points)

  def create_halfspace_from_vector(self, normalVector: np.ndarray, b: float) -> Halfspace2D: # crea un semiespacio
    return Halfspace2D(normalVector = normalVector, b = b)

  def get_dimension(self) -> int: # retorna la dimensión
    return 2

  def _get_polytope_vertices_CCW(self, subregionPolytope: 'Polytope') -> list[list[float]]:
    # Extrae y ordena los vértices del politopo en sentido antihorario (CCW).
    vertices = subregionPolytope.get_vertices() # obtengo los vértices del politopo
    if vertices is None or len(vertices) < 3:
        return vertices.tolist() if vertices is not None else []
    hull = ConvexHull(vertices) # ordenamos los vértices en sentido antihorario con ConvexHull
    sortedVertices = vertices[hull.vertices]
    return sortedVertices.tolist()

  def create_halfspaces_list(self, subregionPolytope: 'Polytope') -> list[Halfspace2D]:
    sortedVertices = self._get_polytope_vertices_CCW(subregionPolytope)    
    numVertices = len(sortedVertices)
    halfspaces = []
    for i in range(numVertices): # iteramos para armar los bordes del politopo (v1, v2)
      v1 = sortedVertices[i]
      v2 = sortedVertices[(i + 1) % numVertices]
      p1 = self.create_point(tuple(v1))
      p2 = self.create_point(tuple(v2))
      hs = self.create_halfspace((p1, p2))
      halfspaces.append(hs)
    return halfspaces

  def get_polytope_edges(self, polytope: 'Polytope') -> list['Edge']:
    # devuelve una lista de las aristas de un politopo como una lista de (Point2D, Point2D)
    edges = polytope.get_edges()
    geomEdges = []
    for e in edges:
      v1, v2 = Point2D(x = e[0][0], y = e[0][1]), Point2D(x = e[1][0], y = e[1][1])
      geomEdges.append((v1, v2))
    return geomEdges