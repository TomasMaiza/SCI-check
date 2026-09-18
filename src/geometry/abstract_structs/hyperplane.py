from abc import ABC, abstractmethod
import numpy as np
from typing import Optional
from geometry.abstract_structs.point import AbstractPoint
from fractions import Fraction

class Hyperplane:
  # representación de un hiperplano  
  def __init__(self, points: list[float]):
        # 2 puntos para un hiperplano (recta) si la dimensión ambiental es 2
        # 3 puntos para un hiperplano (plano) si la dimensión ambiental es 3
    self._points = points

  def get_points(self) -> list[float]:
    return self._points