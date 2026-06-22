from geometry.abstract_structs.simplex import AbstractSimplex
from .point2d import Point2D
import numpy as np
from dataclasses import dataclass

@dataclass(frozen=True)
class Triangle2D(AbstractSimplex):
  # clase para representar el triángulo en 2D

  v1: Point2D # vértices
  v2: Point2D
  v3: Point2D
    
  def get_vertices(self) -> tuple[Point2D, Point2D, Point2D]: # retorna sus vértices
    return (self.v1, self.v2, self.v3)

  def get_edges(self) -> tuple[tuple[Point2D, Point2D], tuple[Point2D, Point2D], tuple[Point2D, Point2D]]: 
    # retorna sus aristas
    # cada arista es una tupla de dos puntos
    return ((self.v1, self.v2), (self.v2, self.v3), (self.v3, self.v1))