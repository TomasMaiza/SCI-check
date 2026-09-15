from geometry.structs_2d import *
from .attene import AtteneAdapter
from bindings import pyattene

class AtteneAdapter2D(AtteneAdapter):
  # clase de adaptador 2d para la librería de implicit predicates

  def create_explicit_point(self, point: Point2D): 
    # crea un punto explícito
    return pyattene.ExplicitPoint2D(point.x, point.y)

  def create_explicit_points_from_halfspace(self, hs: Halfspace2D): 
    # retorna los puntos explícitos que definen un semiespacio
    a, b = hs.get_points()
    aExp = pyattene.ExplicitPoint2D(a.x, a.y)
    bExp = pyattene.ExplicitPoint2D(b.x, b.y)
    return aExp, bExp

  def create_implicit_point_ssi(self, 
                                p1: Point2D, 
                                p2: Point2D, 
                                hs: Halfspace2D): 
    # crea un punto implícito SSI
    p1Exp = pyattene.ExplicitPoint2D(p1.x, p1.y)
    p2Exp = pyattene.ExplicitPoint2D(p2.x, p2.y)
    hs1Exp, hs2Exp = self.create_explicit_points_from_halfspace(hs)
    return pyattene.ImplicitPoint2D_SSI(p1Exp, p2Exp, hs1Exp, hs2Exp)
  
  def orient2d_IEE(self, pImp, ref: Halfspace2D) -> int:
    # calcula la orientación de pImp respecto a la recta ref
    aExp, bExp = self.create_explicit_points_from_halfspace(ref) 
    return pyattene.orient2d_IEE(pImp, aExp, bExp)