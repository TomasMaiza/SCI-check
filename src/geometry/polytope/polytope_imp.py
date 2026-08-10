from abc import ABC, abstractmethod
import numpy as np
from typing import Optional
from .polytope import AbstractPolytope
import polytope as pc
from geometry import AbstractPoint, AbstractHalfspace

class PolytopeImp:
  # implementación de politopos usando la librería polytope

  def __init__(self, 
               vertices: Optional['tuple[AbstractPoint, ...]'] = None, 
               A: Optional['np.ndarray'] = None, 
               b: Optional['np.ndarray'] = None):
    if A is not None and b is not None and vertices is None:
      self._poly = pc.Polytope(A, b)
    elif A is None and b is None and vertices is not None:
      pointsArray = np.array([[v.x, v.y] for v in vertices])
      self._poly = pc.qhull(pointsArray)    
    else:
      raise ValueError("Inicialización inválida: Proveer vértices o (A, b)")