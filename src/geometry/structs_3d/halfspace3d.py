from geometry.abstract_structs.halfspace import AbstractHalfspace
from .point3d import Point3D
import numpy as np
from typing import Optional
from fractions import Fraction

class Halfspace3D(AbstractHalfspace):
  # representación de un semiespacio en 2D
  p1: Point3D
  p2: Point3D
  p3: Point3D

  def __init__(self, 
               points: Optional['tuple[Point3D, Point3D, Point3D]'] = None, 
               normalVector: Optional[np.ndarray] = None, 
               b: Optional[float] = None):
    if normalVector is None and b is None and points is not None:
      self.p1 = points[0]
      self.p2 = points[1]
      self.p3 = points[2]
    elif points is None and normalVector is not None and b is not None:
      self.create_from_normal_vector(normalVector, b)
    else:
      raise ValueError("Inicialización inválida: Proveer (p1, p2, p3) o (normalVector, b).")

  def get_points(self) -> tuple[Point3D, Point3D, Point3D]: 
    return self.p1, self.p2, self.p3

  def create_from_normal_vector(self, normalVector: np.ndarray, b: float):
    # crea un semiespacio a partir de la representación vectorial (Ax <= b).
    basePoint = (b / np.dot(normalVector, normalVector)) * normalVector
    if abs(normalVector[0]) > abs(normalVector[1]):
      aux = np.array([0.0, 1.0, 0.0])
    else:
      aux = np.array([1.0, 0.0, 0.0])
          
    perpVector1 = np.cross(normalVector, aux)
    perpVector2 = np.cross(normalVector, perpVector1)
      
    self.p1 = Point3D(basePoint[0], basePoint[1], basePoint[2])
      
    p2_coords = basePoint + perpVector1
    self.p2 = Point3D(p2_coords[0], p2_coords[1], p2_coords[2])
      
    p3_coords = basePoint + perpVector2
    self.p3 = Point3D(p3_coords[0], p3_coords[1], p3_coords[2])

  def get_normal(self) -> tuple[Fraction, Fraction, Fraction]: # permite obtener el vector normal del semiespacio
    x1, y1, z1 = Fraction(self.p1.x), Fraction(self.p1.y), Fraction(self.p1.z)
    x2, y2, z2 = Fraction(self.p2.x), Fraction(self.p2.y), Fraction(self.p2.z)
    x3, y3, z3 = Fraction(self.p3.x), Fraction(self.p3.y), Fraction(self.p3.z)
            
    nx = (y2 - y1) * (z3 - z1) - (z2 - z1) * (y3 - y1)
    ny = (z2 - z1) * (x3 - x1) - (x2 - x1) * (z3 - z1)
    nz = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
    return nx, ny, nz