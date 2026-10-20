from abc import ABC, abstractmethod
import numpy as np
import numpy.typing as npt
from affine_system import *

class ApproximationStrategy(ABC):
  @abstractmethod
  def apply(self, s: float, x: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    # aplica la función de aproximación
    pass

  @abstractmethod
  def error_bound(self, r: float, tau: float) -> float:
    # calcula el error de la aproximación
    pass

  @abstractmethod
  def error_sequence(self, h: float, K: int) -> list[float]:
    # calcula la secuencia de errores para el método
    pass

  @abstractmethod
  def get_matrix(self, s: float) -> npt.NDArray[np.float64]:
    # calcula la matriz de la aproximación tomando el paso s
    pass