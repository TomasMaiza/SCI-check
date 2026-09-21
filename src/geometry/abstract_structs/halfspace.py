import numpy as np
from typing import Optional, TYPE_CHECKING
from geometry.abstract_structs.point import AbstractPoint
from fractions import Fraction

if TYPE_CHECKING:
    from src.common.types import Point

class Halfspace():
  # representación de un semiespacio en un espacio n-dimensional

  _points: list['Point']
  _normal: np.ndarray
  _b: float

  def __init__(self, 
               points: Optional['list[Point]'] = None, 
               normalVector: Optional[np.ndarray] = None, 
               b: Optional[float] = None):
    if normalVector is None and b is None and points is not None:
      self._points = points
    elif points is None and normalVector is not None and b is not None:
      self.create_from_normal_vector(normalVector, b)
    else:
      raise ValueError("Inicialización inválida: Proveer puntos o (normalVector, b).")

  def get_points(self) -> list['Point']: # retorna los puntos que definen el semiespacio
    return self._points

  def create_from_normal_vector(self, normalVector: np.ndarray, b: float): 
    # permite crear el semiespacio a partir del vector normal
    self._normal = normalVector
    self._b = b

  def get_normal(self) -> np.ndarray: # permite obtener el vector normal del semiespacio
    if self._normal is not None:
      return self._normal
    p0 = self._points[0]
    vectors = self._points[1:] - p0
    # SVD descompone la matriz. La última fila de Vh es siempre ortogonal a vectors
    _, _, Vh = np.linalg.svd(vectors)
    self._normal = Vh[-1]
    self._b = np.dot(self._normal, p0)
    return self._normal