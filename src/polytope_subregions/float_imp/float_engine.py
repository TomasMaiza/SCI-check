from affine_system import AffineMode
from geometry import Polytope
import numpy as np
from .matrices import partition_matrices, partition_matrices_bound
from .approximations import Euler, Taylor
from polytope_subregions.engine_strategy import EngineStrategy

class FloatEngine(EngineStrategy):
  _approxMethodDict = {"Euler": Euler, "Taylor": Taylor}

  def __init__(self, approxMethodName: str):
    # permite inicializar el motor con el método deseado (es decir, se setea en subregions)
    self.approxMethod = self._approxMethodDict[approxMethodName]

  def partition_matrices(self,
                         polytope: Polytope, 
                         subsystem: AffineMode, 
                         h: float) -> tuple[np.ndarray, np.ndarray]:
    return partition_matrices(polytope, subsystem, h)

  def partition_matrices_bound(self, 
                               polytope: Polytope, 
                               r: float, 
                               midErrorBound: float) -> np.ndarray:
    return partition_matrices_bound(polytope, r, midErrorBound)