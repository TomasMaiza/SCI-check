import numpy as np
import numpy.typing as npt
import polytope as pc
from .strategy import ApproximationStrategy
from affine_system import *
from polytope_subregions.matrices import sas_augmented_matrix, augmented_x
from math import factorial

class Taylor(ApproximationStrategy):
  def __init__(self, 
               subsystem: AffineMode, 
               polytope: pc.Polytope,
               scaling: int,
               order: int):
    # Inicializa la función de aproximación y la función de error
    self._A, self._b = subsystem.get_subsystem()
    self._homA = sas_augmented_matrix(subsystem)
    self._S = pc.extreme(polytope)
    self._s = scaling
    self._M = order
    verticesAug = np.hstack((self._S, np.ones((self._S.shape[0], 1))))
    self._R_S = float(np.max(np.linalg.norm(verticesAug, ord=2, axis=1)))
  
  def apply(self, h: float, s: int, order: int, x: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    # aplica la función de aproximación
    homx = augmented_x(x)
    Phi = self.get_matrix(h, s, order)
    return Phi @ homx

  def error_bound(self, r: float, tau: float) -> float:
    # calcula el error de la aproximación
    normA = np.linalg.norm(self._A, ord=2)
    M = self._get_M(normA)
    return r * (1 + normA * tau) + M * (np.exp(normA * tau) - 1 - normA * tau)
  
  def _get_M(self, normA: float):
    # auxiliar para calcular M
    if normA < 1e-12:
      return 0.0
    m = -1 # vamos a calcular el valor máximo de una norma así que inicio en un número negativo
    for x in self._S:
      x = x.reshape(-1, 1) # forzamos a x a ser un vector columna
      norm = np.linalg.norm(self._A @ x + self._b, ord=2)
      if norm > m:
        m = norm
    return 1/normA * m

  def error_sequence(self, h: float, K: int) -> list[float]:
    # calcula la secuencia de errores para el método
    normHomA = np.linalg.norm(self._homA, ord=2)
    Cerr = self._get_C_err(normHomA, h)
    errorSeq = []
    for k in range(0, K + 1):
      r = k * Cerr * np.exp(normHomA * h * k)
      errorSeq.append(r)
    return errorSeq

  def _get_C_err(self, normHomA: float, h: float):
    num = (h * normHomA)**(self._M + 1) * self._R_S
    den = self._s**self._M * factorial(self._M + 1)
    return num / den
  
  def get_matrix(self, h: float, s: int, order: int) -> npt.NDArray[np.float64]:
    # calcula la matriz de la aproximación tomando el paso s
    tau = h / s
    dim = self._homA.shape[0]
    I = np.eye(dim, dtype=np.float64)
    Q = I.copy()
    term = I.copy()
    for j in range(1, order + 1):
      term = term @ (self._homA * tau) / j
      Q = Q + term
            
    # Squaring: Elevamos la matriz del micro-paso a la potencia s
    return np.linalg.matrix_power(Q, s)