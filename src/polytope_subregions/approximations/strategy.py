from abc import ABC, abstractmethod
import numpy as np
import numpy.typing as npt
from affine_system import *

class ApproximationStrategy(ABC):
  @abstractmethod
  def __init__(self, subsystem: AffineMode):
    # Inicializa la función de aproximación y la función de error
    pass

  @abstractmethod
  def apply_approx(self, s: float, x: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    # aplica la función de aproximación
    pass

  @abstractmethod
  def error_bound(self, r: float, tau: float) -> float:
    # calcula el error de la aproximación
    pass