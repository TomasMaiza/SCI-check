import numpy as np
import numpy.typing as npt
from .strategy import ApproximationStrategy
from affine_system import *
from polytope_subregions.matrices import sas_augmented_matrix
from geometry import Polytope

class Euler(ApproximationStrategy):
  def __init__(self, subsystem: AffineMode, polytope: Polytope):
    # Inicializa la función de aproximación y la función de error
    self._A, self._b = subsystem.get_subsystem()
    self._homA = sas_augmented_matrix(subsystem)
    self._S = polytope.get_vertices()
  
  def apply(self, s: float, x: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    # aplica la función de aproximación
    return x + s * (self._A @ x + self._b) # el @ hace el producto matricial
  
  def error_bound(self, r: float, tau: float) -> float:
    # calcula el error de la aproximación
    normA = float(np.linalg.norm(self._A, ord=2))
    M = self._get_M(normA)
    return r * (1 + normA * tau) + M * (np.exp(normA * tau) - 1 - normA * tau)

  def _get_M(self, normA: float) -> float:
    # auxiliar para calcular M
    if normA < 1e-12:
      return 0.0
    m = -1 # vamos a calcular el valor máximo de una norma así que inicio en un número negativo
    for x in self._S:
      x = x.reshape(-1, 1) # forzamos a x a ser un vector columna
      norm = np.linalg.norm(self._A @ x + self._b, ord=2)
      if norm > m:
        m = norm
    return float(1/normA * m)

  def error_sequence(self, h: float, K: int) -> list[float]:
    # calcula la secuencia de errores para el método
    errorSeq = []
    r = 0 # r0
    for k in range(0, K):
      errorSeq.append(r)
      r = self.error_bound(r, abs(h))
    errorSeq.append(r) # appendeamos r_k
    return errorSeq

  def get_matrix(self, s: float) -> npt.NDArray[np.float64]:
    # calcula la matriz de la aproximación tomando el paso s con la matriz aumentada
    dim = self._homA.shape[0]
    I = np.eye(dim, dtype=np.float64)
    return I + s * self._homA