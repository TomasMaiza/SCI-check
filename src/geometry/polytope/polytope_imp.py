from abc import ABC, abstractmethod
import numpy as np
from typing import Optional
from .polytope import Polytope
import polytope as pc
from scipy.spatial import ConvexHull
from geometry import AbstractPoint, AbstractHalfspace

class PolytopeImp(Polytope):
  # implementación de politopos usando la librería polytope
  polytope: pc.Polytope

  def __init__(self, 
               vertices: Optional['tuple[AbstractPoint, ...]'] = None, 
               A: Optional['np.ndarray'] = None, 
               b: Optional['np.ndarray'] = None):
    if A is not None and b is not None and vertices is None:
      self.polytope = pc.Polytope(A, b)
    elif A is None and b is None and vertices is not None and len(vertices) > 2:
      pointsArray = np.array([[v.x, v.y] for v in vertices])
      self.polytope = pc.qhull(pointsArray)    
    else:
      raise ValueError("Inicialización inválida: Proveer vértices o (A, b)")
    
  def get_vertices(self) -> np.ndarray:
    # permite obtener los vértices del politopo
    return pc.extreme(self.polytope)
  
  def get_hrep(self) -> tuple[np.ndarray, np.ndarray]:
    # permite obtener las matrices A y b que definen al politopo
    return self.polytope.A, self.polytope.b
  

  def _map_polytopes_from_pc(self, pcList: list[pc.Polytope]) -> 'PolytopeImp':
    # toma una lista de pc.Polytope y retorna una de PolytopeImp
    polyList = []
    for p in pcList:
      A, b = p.A, p.b
      polyList.append(PolytopeImp(A = A, b = b))
    return polyList

  def intersect(self, p: 'PolytopeImp') -> list['PolytopeImp']:
    # permite intersecar el politopo con otro
    pc = p.polytope
    intPoly = self.polytope.intersect(pc)
    return PolytopeImp(A = intPoly.A, b = intPoly.b)

  def union(self, p: 'PolytopeImp') -> list['PolytopeImp']:
    # permite calcular la unión del politopo con otro
    # retorna una lista por si la región resultante no es convexa
    pcList = self.polytope.union(p.polytope)
    return self._map_polytopes_from_pc(pcList)

  def difference(self, p: 'PolytopeImp') -> list['PolytopeImp']:
    # permite calcular la diferencia entre dos politopos
    pcList = self.polytope.diff(p.polytope)
    return self._map_polytopes_from_pc(pcList)

  def is_empty(self) -> bool:
    # retorna si el politopo es vacío
    return pc.is_empty(self.polytope)

  def contains(self, x: AbstractPoint):
    # retorna si un punto pertenece al politopo
    point = x.get_point()
    return point in self.polytope

  def subset(self, p: 'PolytopeImp') -> bool:
    # retorna si el politopo es subconjunto de p
    return pc.is_subset(self.polytope, p.polytope)

  def reduce(self):
    # elimina las inecuaciones redundantes
    pc.reduce(self.polytope)

