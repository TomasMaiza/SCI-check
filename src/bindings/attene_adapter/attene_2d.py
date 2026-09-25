from geometry import Halfspace
from .attene import AtteneAdapter
from bindings import pyattene
from common import Point

class AtteneAdapter2D(AtteneAdapter):
  # clase de adaptador 2d para la librería de implicit predicates

  def create_explicit_point(self, point: Point): 
    # crea un punto explícito
    return pyattene.ExplicitPoint2D(point[0], point[1])

  def create_explicit_points_from_halfspace(self, hs: Halfspace): 
    # retorna los puntos explícitos que definen un semiespacio
    points = hs.get_points()
    a, b = points[0], points[1]
    aExp = pyattene.ExplicitPoint2D(a[0], a[1])
    bExp = pyattene.ExplicitPoint2D(b[0], b[1])
    return aExp, bExp

  def create_implicit_point_ssi(self, 
                                p1: Point, 
                                p2: Point, 
                                hs: Halfspace): 
    # crea un punto implícito SSI
    p1Exp = pyattene.ExplicitPoint2D(p1[0], p1[1])
    p2Exp = pyattene.ExplicitPoint2D(p2[0], p2[1])
    hs1Exp, hs2Exp = self.create_explicit_points_from_halfspace(hs)
    return pyattene.ImplicitPoint2D_SSI(p1Exp, p2Exp, hs1Exp, hs2Exp)
  
  def orient2d_IEE(self, pImp, ref: Halfspace) -> int:
    # calcula la orientación de pImp respecto a la recta ref
    aExp, bExp = self.create_explicit_points_from_halfspace(ref) 
    return pyattene.orient2d_IEE(pImp, aExp, bExp)

  def orient2d_EEE(self, p: Point, ref: Halfspace) -> int:
    # calcula la orientación del punto explícito p respecto a la recta ref
    pExp = pyattene.ExplicitPoint2D(p[0], p[1])
    aExp, bExp = self.create_explicit_points_from_halfspace(ref)
    return pyattene.orient2d_EEE(pExp, aExp, bExp)