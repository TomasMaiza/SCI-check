from dataclasses import dataclass
from typing import Dict, List
import numpy as np
import numpy.typing as npt
from .affine_mode import AffineMode

@dataclass(frozen=True)
class SwitchedAffineSystem:
  # Representa el sistema completo con todos sus modos disponibles.
  def __init__(self, modesDict: Dict[int, (npt.NDArray[np.float64], npt.NDArray[np.float64])]):
    for i in modesDict.keys():
      A, b = modesDict[i]
      self._modes[i] = AffineMode(A, b) # diccionario para mapear un modo a su sistema afín
    
  def get_mode(self, mode: int) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    return self._modes[mode].get_system()