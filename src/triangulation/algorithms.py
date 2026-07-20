import numpy as np
from scipy.spatial import Delaunay
from .strategy import TriangulationAlgorithm

class DelaunayTriangulation(TriangulationAlgorithm):
  def triangulate(self, vertices: np.ndarray) -> list[np.ndarray]:
    triangles = Delaunay(vertices)
    return [vertices[simplex] for simplex in triangles.simplices] 
  
class FanTriangulation(TriangulationAlgorithm):
  def triangulate(self, vertices: np.ndarray) -> list[np.ndarray]:
    # DEBERÍAN ORDENARSE LOS VÉRTICES
    lenv = len(vertices)
    triangles = []
    v0 = vertices[0]
    for i in range(1, lenv - 1):
      triangles.append(np.array([v0, vertices[i], vertices[i + 1]]))
    return triangles