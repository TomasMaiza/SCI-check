from geometry.structs_3d import *
from .attene import AtteneAdapter
from bindings import pyattene

class AtteneAdapter3D(AtteneAdapter):
  # clase de adaptador 2d para la librería de implicit predicates

  def create_explicit_point(self, point: Point3D): 
    # crea un punto explícito
    return pyattene.ExplicitPoint3D(point.x, point.y, point.z)

  def create_explicit_points_from_halfspace(self, hs: Halfspace3D): 
    # retorna los puntos explícitos que definen un semiespacio
    a, b, c = hs.get_points()
    aExp = pyattene.ExplicitPoint3D(a.x, a.y, a.z)
    bExp = pyattene.ExplicitPoint3D(b.x, b.y, b.z)
    cExp = pyattene.ExplicitPoint3D(c.x, c.y, c.z)
    return aExp, bExp, cExp

  def create_implicit_point_lpi(self, 
                                p1: Point3D, 
                                p2: Point3D, 
                                plane: Halfspace3D): 
    # crea un punto implícito LPI (intersección de p1p2 con plane)
    p1Exp = pyattene.ExplicitPoint3D(p1.x, p1.y, p1.z)
    p2Exp = pyattene.ExplicitPoint3D(p2.x, p2.y, p2.z)
    aExp, bExp, cExp = self.create_explicit_points_from_halfspace(plane)
    return pyattene.ImplicitPoint3D_LPI(p1Exp, p2Exp, aExp, bExp, cExp)

  def create_implicit_point_tpi(self, 
                                p1: Halfspace3D, 
                                p2: Halfspace3D, 
                                p3: Halfspace3D): 
    # crea un punto implícito TPI (intersección de los tres planos)
    aExp, bExp, cExp = self.create_explicit_points_from_halfspace(p1)
    dExp, eExp, fExp = self.create_explicit_points_from_halfspace(p2)
    gExp, hExp, iExp = self.create_explicit_points_from_halfspace(p3)
    return pyattene.ImplicitPoint3D_TPI(aExp, bExp, cExp,
                                        dExp, eExp, fExp,
                                        gExp, hExp, iExp)

  def orient3dE(self, 
                p: Point3D,
                f: Halfspace3D) -> int:
    # calcula la orientación del punto explícito p respecto al plano f
    pExp = pyattene.ExplicitPoint3D(p.x, p.y, p.z)
    aExp, bExp, cExp = self.create_explicit_points_from_halfspace(f)
    return pyattene.orient3d(aExp, bExp, cExp, pExp)

  def orient3dI(self, 
                pImp,
                f: Halfspace3D) -> int:
    # calcula la orientación del punto implícito p respecto al plano f
    aExp, bExp, cExp = self.create_explicit_points_from_halfspace(f)
    return pyattene.orient3d(aExp, bExp, cExp, pImp)