import numpy as np
from geometry.abstract_structs.point import AbstractPoint
from fractions import Fraction
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from src.common.types import Point

class Hyperplane:
  # representación de un hiperplano  
  def __init__(self, points: list['Point']):
        # 2 puntos para un hiperplano (recta) si la dimensión ambiental es 2
        # 3 puntos para un hiperplano (plano) si la dimensión ambiental es 3
    self._points = points

  def get_points(self) -> list['Point']:
    return self._points