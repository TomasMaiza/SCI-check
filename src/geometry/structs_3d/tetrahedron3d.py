from geometry.abstract_structs.simplex import AbstractSimplex
from .point3d import Point3D
from .triangle3d import Triangle3D
import numpy as np
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.common.types import Edge

class Tetrahedron3D(AbstractSimplex):
  # clase para representar el tetraedro en 3D

  v1: Point3D # vértices
  v2: Point3D
  v3: Point3D
  v4: Point3D
  _triangles: list[Triangle3D]

  def __init__(self, vertices: tuple[Point3D, Point3D, Point3D, Point3D]):
    self.v1 = vertices[0]
    self.v2 = vertices[1]
    self.v3 = vertices[2]
    self.v4 = vertices[3]
    self._get_triangles()
    
  def get_vertices(self) -> tuple[Point3D, Point3D, Point3D, Point3D]: # retorna sus vértices
    return (self.v1, self.v2, self.v3, self.v4)

  def _get_triangles(self):
    from coverage_checker import pyattene
    self._triangles = []
    v0, v1, v2, v3 = self.get_vertices() 
    combinations = [
            ((v0, v1, v2), v3),
            ((v0, v1, v3), v2),
            ((v0, v2, v3), v1),
            ((v1, v2, v3), v0)
    ]
        
    for (A, B, C), D in combinations:
      aExp = pyattene.ExplicitPoint3D(A.x, A.y, A.z)
      bExp = pyattene.ExplicitPoint3D(B.x, B.y, B.z)
      cExp = pyattene.ExplicitPoint3D(C.x, C.y, C.z)
      dExp = pyattene.ExplicitPoint3D(D.x, D.y, D.z)
            
      # Evaluamos de qué lado del plano ABC está el vértice opuesto D
      ori = pyattene.orient3d(dExp, aExp, bExp, cExp)

      if ori == 1:
        face = Triangle3D(A, C, B) 
      elif ori == -1:
        face = Triangle3D(A, B, C)   
      else:
        raise ValueError("Tetraedro degenerado: los 4 vértices son coplanares.")
      self._triangles.append(face)
            
    return self._triangles

  def get_faces(self) -> tuple[Triangle3D, Triangle3D, Triangle3D, Triangle3D]:
    return tuple(self._triangles)

  def get_edges(self) -> tuple['Edge', ...]: # retorna sus aristas
    return (
          (self.v1, self.v2),
          (self.v1, self.v3),
          (self.v1, self.v4),
          (self.v2, self.v3),
          (self.v2, self.v4),
          (self.v3, self.v4)
      )

  def get_inverse_edges(self) -> tuple['Edge', ...]:
    # retorna las aristas con el sentido invertido
    pass

  def get_all_edges(self) -> tuple[tuple['Edge', ...], tuple['Edge', ...]]:
    # retorna las aristas en ambos sentidos
    pass