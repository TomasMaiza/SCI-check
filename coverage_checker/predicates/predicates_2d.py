from common import OrientResult, IN, ON, OUT
from geometry.structs_2d import *
from .predicates import AbstractPredicates
from shewchuk import orientation
from .. import pyattene

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
    # queremos calcular la orientación de f1 \cap rs respecto a f2
    
    rExp = pyattene.ExplicitPoint2D(r.x, r.y)
    sExp = pyattene.ExplicitPoint2D(s.x, s.y)

    tExp = pyattene.ExplicitPoint2D(t.x, t.y)
    uExp = pyattene.ExplicitPoint2D(u.x, u.y)

    aExp = pyattene.ExplicitPoint2D(a.x, a.y)
    bExp = pyattene.ExplicitPoint2D(b.x, b.y)

    # Punto implícito: intersección de rs con tu
    pImp = pyattene.ImplicitPoint2D_SSI(rExp, sExp, tExp, uExp)

    ori = pyattene.orient2d_IEE(pImp, aExp, bExp)

    if ori == -1:
      ret = OrientResult.OUT
    elif ori == 0:
      ret = OrientResult.ON
    else:
      ret = OrientResult.IN
    return ret

  def orient_TPI(self) -> OrientResult: # retorna IN, OUT, ON
    pass