from dataclasses import dataclass
import numpy as np
import numpy.typing as npt

@dataclass(frozen=True)
class AffineMode:
  # Representa un único modo x_dot = A_i*x + b_i
  A: npt.NDArray[np.float64]
  b: npt.NDArray[np.float64]

  def __post_init__(self):
    # validamos dimensiones de las matrices
    if self.A.ndim != 2 or self.A.shape[0] != self.A.shape[1]:
      raise ValueError(f"La matriz A debe ser cuadrada (n x n)")
    
    n = self.A.shape[0]
        
    if self.b.shape != (n, 1):
      raise ValueError(f"El vector b debe ser un vector columna ({n}, 1)")

  def get_subsystem(self) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    return (self.A, self.b)