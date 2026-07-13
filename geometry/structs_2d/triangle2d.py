from geometry.abstract_structs.simplex import AbstractSimplex
from .point2d import Point2D
import numpy as np
from dataclasses import dataclass
from common.types import Edge

@dataclass(frozen=True)
class Triangle2D(AbstractSimplex):
  # clase para representar el triángulo en 2D

  v1: Point2D # vértices
  v2: Point2D
  v3: Point2D
    
  def get_vertices(self) -> tuple[Point2D, Point2D, Point2D]: # retorna sus vértices
    return (self.v1, self.v2, self.v3)

  def get_edges(self) -> tuple[Edge, Edge, Edge]: 
    # retorna sus aristas
    # cada arista es una tupla de dos puntos
    return ((self.v1, self.v2), (self.v2, self.v3), (self.v3, self.v1))

  def get_inverse_edges(self):
    # retorna las aristas con el sentido invertido
    return ((self.v2, self.v1), (self.v3, self.v2), (self.v1, self.v3))

  def get_all_edges(self):
    # retorna las aristas en ambos sentidos
    return self.get_edges(), self.get_inverse_edges()