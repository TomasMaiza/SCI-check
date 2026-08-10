import numpy as np
from .strategy import TriangulationAlgorithm
from geometry import Polytope

class PolytopeTriangulator:
  def __init__(self, strategy: TriangulationAlgorithm) -> None:
    self._strategy = strategy
  
  def set_strategy(self, new_strategy: TriangulationAlgorithm) -> None:
    self._strategy = new_strategy

  def triangulate(self, polytope: Polytope) -> list[np.ndarray]:
    vertices = polytope.get_vertices()
    if vertices is None or len(vertices) < 3:
      raise ValueError("No se puede triangular un polígono con menos de 3 vértices.")

    triangles = self._strategy.triangulate(vertices)
    return triangles