from common import OrientResult, IN, ON, OUT
from geometry.structs_2d import *
from geometry import Polytope
from .predicates import AbstractPredicates
from shewchuk import orientation
from .. import pyattene

class Predicates2d(AbstractPredicates):
  # clase para implementar los predicados en 2d

  def orient(self, v: Point2D, f: Halfspace2D) -> OrientResult: # retorna IN, OUT, ON
    a, b = f.get_points()
    ori = orientation(a.x, a.y, b.x, b.y, v.x, v.y)

    if ori == 1:
      ret = OrientResult.IN
    elif ori == 0:
      ret = OrientResult.ON
    else:
      ret = OrientResult.OUT
    return ret

  def orient_LPI(self, r: Point2D, s: Point2D, f1: Halfspace2D, ref: Halfspace2D) -> OrientResult: # retorna IN, OUT, ON
    t, u = f1.get_points()
    a, b = ref.get_points()
    # queremos calcular la orientación de f1 \cap rs respecto a ref
    
    rExp = pyattene.ExplicitPoint2D(r.x, r.y)
    sExp = pyattene.ExplicitPoint2D(s.x, s.y)

    tExp = pyattene.ExplicitPoint2D(t.x, t.y)
    uExp = pyattene.ExplicitPoint2D(u.x, u.y)

    aExp = pyattene.ExplicitPoint2D(a.x, a.y)
    bExp = pyattene.ExplicitPoint2D(b.x, b.y)

    # Punto implícito: intersección de rs con tu
    pImp = pyattene.ImplicitPoint2D_SSI(rExp, sExp, tExp, uExp)

    ori = pyattene.orient2d_IEE(pImp, aExp, bExp)

    if ori == 1:
      ret = OrientResult.IN
    elif ori == 0:
      ret = OrientResult.ON
    else:
      ret = OrientResult.OUT
    return ret

  def orient_TPI(self, 
                 triangle: Triangle2D, 
                 f1: Halfspace2D, 
                 f2: Halfspace2D, 
                 ref: Halfspace2D) -> OrientResult: # retorna IN, OUT, ON
    r, s = f1.get_points()
    return self.orient_LPI(r, s, f2, ref)

  def implicit_point_in_polytope(self, 
                                 polytope: Polytope, 
                                 f1: Halfspace2D, 
                                 f2: Halfspace2D) -> bool: 
    # determina si un punto (intersección de dos semiespacios) pertenece a un triángulo
    edges = polytope.get_edges()
    r, s = f1.get_points()
    ret = True
    for e in edges:
      # queremos calcular la orientación de f1 \cap f2 respecto a v1v2
      p1, p2 = Point2D(e[0][0], e[0][1]), Point2D(e[1][0], e[1][1])
      face = Halfspace2D(points = (p1, p2))
      ori = self.orient_LPI(r, s, f2, e)
      if ori != IN:
        ret = False
        break
    return ret