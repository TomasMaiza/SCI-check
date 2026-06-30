import numpy as np
from common.enums import OrientResult
from geometry.structs_2d.point2d import Point2D
from geometry.structs_2d.lpipoint2d import LPIPoint2D
from geometry.structs_2d.halfspace2d import Halfspace2D
from .predicates import AbstractPredicates
from shewchuk import orientation, vectors_cross_product

IN = OrientResult.IN
OUT = OrientResult.OUT
ON = OrientResult.ON

class Predicates2d(AbstractPredicates):
  # clase para implementar los predicados en 2d

  def orient(self, v: Point2D, f: Halfspace2D) -> OrientResult: # retorna IN, OUT, ON
    a, b = f.get_points()
    ori = orientation(a.x, a.y, b.x, b.y, v.x, v.y)

    if ori == -1:
      ret = OrientResult.OUT
    elif ori == 0:
      ret = OrientResult.ON
    else:
      ret = OrientResult.IN
    return ret

  def orient_LPI(self, r: Point2D, s: Point2D, f1: Halfspace2D, f2: Halfspace2D) -> OrientResult: # retorna IN, OUT, ON
    t, u = f1.get_points()
    a, b = f2.get_points()

    beta = vectors_cross_product(s.x, s.y, r.x, r.y, t.x, t.y, u.x, u.y)

    if beta == 0:
      return OUT

    alpha = vectors_cross_product(t.x, t.y, r.x, r.y, t.x, t.y, u.x, u.y)

    O = beta * vectors_cross_product(a.x, a.y, b.x, b.y, a.x, a.y, r.x, r.y) 
    + alpha * vectors_cross_product(a.x, a.y, b.x, b.y, r.x, r.y, s.x, s.y)

    if beta < 0:
      O = -O

    if O > 0:
      return IN
    return OUT

  def orient_TPI(self) -> OrientResult: # retorna IN, OUT, ON
    pass