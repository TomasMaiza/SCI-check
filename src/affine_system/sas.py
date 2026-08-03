from typing import Dict, List
import numpy as np
import numpy.typing as npt
from .affine_mode import AffineMode

class SwitchedAffineSystem:
  # Representa el sistema completo con todos sus modos disponibles.
  def __init__(self, modesDict: Dict[int, tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]]):
    if not modesDict:
      raise ValueError("El sistema debe contener al menos un modo.")
    first = True # para tomar la dimensión del primer modo como referencia
    self._modes = {}
    for i in modesDict.keys():
      A, b = modesDict[i]
      if first:
        expectedDimension = A.shape[0]
        first = False
      dimension = A.shape[0]
      if dimension != expectedDimension:
        raise ValueError(
                    f"Inconsistencia de dimensiones: El modo {i} tiene "
                    f"dimensión {dimension}, pero se esperaba {expectedDimension}."
                )
      self._modes[i] = AffineMode(A, b) # diccionario para mapear un modo a su sistema afín

  def add_mode(self, modeID: int, subsystem: AffineMode):
    # permite agregar modos manualmente
    if modeID in self._modes.keys():
      raise ValueError(f"Mode {modeID} already in system.")
    self._modes[modeID] = subsystem
    
  def get_mode_matrices(self, mode: int) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    # retorna las matrices A y b del modo indicado
    return self._modes[mode].get_subsystem()

  def get_subsystem(self, mode: int) -> AffineMode:
    # retorna el subsistema del modo indicado  
    return self._modes[mode]

  def get_all_modes(self) -> list[int]:
    # retorna una lista de los modos (índices) del sistema
    return list(self._modes.keys())