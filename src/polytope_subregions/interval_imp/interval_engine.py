from affine_system import AffineMode
from geometry import Polytope
import numpy as np
from polytope_subregions.engine_strategy import EngineStrategy
from juliacall import Main as jl

jl.include("interval_main.jl") # ojo si falla esto

class IntervalEngine(EngineStrategy):
  _approxMethodDict = {"Euler": jl.Euler, "Taylor": jl.Taylor}

  def __init__(self, approxMethodName: str):
    # permite inicializar el motor con el método deseado (es decir, se setea en subregions)
    self.approxMethod = self._approxMethodDict[approxMethodName]

  def partition_matrices(self,
                         polytope: Polytope, 
                         subsystem: AffineMode, 
                         h: float) -> tuple[np.ndarray, np.ndarray]:
    pass

  def partition_matrices_bound(self, 
                               polytope: Polytope, 
                               r: float, 
                               midErrorBound: float) -> np.ndarray:
    pass