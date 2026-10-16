from abc import ABC, abstractmethod
from geometry import Polytope
from affine_system import AffineMode
import numpy.typing as npt
import numpy as np

class EngineStrategy(ABC):
  # clase abstracta para las distintas representaciones de los datos: float, interval, fraction, etc

  @abstractmethod
  def partition_matrices(self, polytope: Polytope, subsystem: AffineMode, h: float) -> tuple[npt.NDArray, npt.NDArray]:
    pass

  @abstractmethod
  def partition_matrices_bound(self, polytope: Polytope, r: float, midErrorBound: float) -> npt.NDArray:
    pass