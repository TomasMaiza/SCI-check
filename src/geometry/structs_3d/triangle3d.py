from geometry.abstract_structs.simplex import AbstractSimplex
from .point3d import Point3D
import numpy as np
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.common.types import Edge

@dataclass(frozen=True)
class Triangle2D(AbstractSimplex):
  # clase para representar el triángulo en 2D

  v1: Point3D # vértices
  v2: Point3D
  v3: Point3D
    
  def get_vertices(self) -> tuple[Point3D, Point3D, Point3D]: # retorna sus vértices
    return (self.v1, self.v2, self.v3)

  def get_edges(self) -> tuple['Edge', 'Edge', 'Edge']: 
    # retorna sus aristas
    # cada arista es una tupla de dos puntos
    return ((self.v1, self.v2), (self.v2, self.v3), (self.v3, self.v1))

  def get_inverse_edges(self) -> tuple['Edge', 'Edge', 'Edge']:
    # retorna las aristas con el sentido invertido
    return ((self.v2, self.v1), (self.v3, self.v2), (self.v1, self.v3))

  def get_all_edges(self) -> tuple[tuple['Edge', 'Edge', 'Edge'], tuple['Edge', 'Edge', 'Edge']]:
    # retorna las aristas en ambos sentidos
    return self.get_edges(), self.get_inverse_edges()