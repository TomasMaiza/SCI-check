import numpy as np
from common.enums import OrientResult
from geometry.structs_2d.point2d import Point2D
from geometry.structs_2d.lpipoint2d import LPIPoint2D
from geometry.structs_2d.halfspace2d import Halfspace2D
from .predicates import AbstractPredicates
from shewchuk import orientation

class Predicates2d(AbstractPredicates):
  # clase para implementar los predicados en 2d

  def orient(self, v: Point2D, f: Halfspace2D) -> OrientResult: # retorna IN, OUT, ON
    a, b = f.get_points()
    ori = orientation(a.x, a.y, b.x, b.y, v.x, v.y)

    if (ori == -1):
      ret = OrientResult.OUT
    else:
      ret = OrientResult.IN
    return ret

  def orient_LPI(self) -> OrientResult: # retorna IN, OUT, ON
    pass

  def orient_TPI(self) -> OrientResult: # retorna IN, OUT, ON
    pass