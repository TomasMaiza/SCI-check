from dataclasses import dataclass
import numpy as np
import numpy.typing as npt

@dataclass(frozen=True)
class AffineMode:
  # Representa un único modo x_dot = A_i*x + b_i
  def __init__(self, A: npt.NDArray[np.float64], b: npt.NDArray[np.float64]):
    self.A = A;
    self.b = b;

  def get_subsystem(self) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    return (self.A, self.b)