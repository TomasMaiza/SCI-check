import polytope as pc
import numpy as np
from .strategy import TriangulationAlgorithm

class PolytopeTriangulator:
  def __init__(self, strategy: TriangulationAlgorithm) -> None:
    self._strategy = strategy
  
  def set_strategy(self, new_strategy: TriangulationAlgorithm) -> None:
    self._strategy = new_strategy

  def triangulate(self, region: pc.Polytope) -> list[np.ndarray]:
    vertices = pc.extreme(region)
    if vertices is None or len(vertices) < 3:
      raise ValueError("No se puede triangular un polígono con menos de 3 vértices.")

    triangles = self._strategy.triangulate(vertices)
    return triangles