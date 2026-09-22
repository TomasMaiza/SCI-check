from geometry.structs_3d import *
from .attene import AtteneAdapter
from bindings import pyattene
from geometry import Halfspace
from common import Point

class AtteneAdapter3D(AtteneAdapter):
  # clase de adaptador 2d para la librería de implicit predicates

  def create_explicit_point(self, point: Point): 
    # crea un punto explícito
    return pyattene.ExplicitPoint3D(point[0], point[1], point[2])

  def create_explicit_points_from_halfspace(self, hs: Halfspace): 
    # retorna los puntos explícitos que definen un semiespacio
    points = hs.get_points()
    a, b, c = points[0], points[1], points[2]
    aExp = pyattene.ExplicitPoint3D(a[0], a[1], a[2])
    bExp = pyattene.ExplicitPoint3D(b[0], b[1], b[2])
    cExp = pyattene.ExplicitPoint3D(c[0], c[1], c[2])
    return aExp, bExp, cExp

  def create_implicit_point_lpi(self, 
                                p1: Point, 
                                p2: Point, 
                                plane: Halfspace): 
    # crea un punto implícito LPI (intersección de p1p2 con plane)
    p1Exp = pyattene.ExplicitPoint3D(p1[0], p1[1], p1[2])
    p2Exp = pyattene.ExplicitPoint3D(p2[0], p2[1], p2[2])
    aExp, bExp, cExp = self.create_explicit_points_from_halfspace(plane)
    return pyattene.ImplicitPoint3D_LPI(p1Exp, p2Exp, aExp, bExp, cExp)

  def create_implicit_point_tpi(self, 
                                p1: Halfspace, 
                                p2: Halfspace, 
                                p3: Halfspace): 
    # crea un punto implícito TPI (intersección de los tres planos)
    aExp, bExp, cExp = self.create_explicit_points_from_halfspace(p1)
    dExp, eExp, fExp = self.create_explicit_points_from_halfspace(p2)
    gExp, hExp, iExp = self.create_explicit_points_from_halfspace(p3)
    return pyattene.ImplicitPoint3D_TPI(aExp, bExp, cExp,
                                        dExp, eExp, fExp,
                                        gExp, hExp, iExp)

  def orient3dE(self, 
                p: Point,
                f: Halfspace) -> int:
    # calcula la orientación del punto explícito p respecto al plano f
    pExp = pyattene.ExplicitPoint3D(p[0], p[1], p[2])
    aExp, bExp, cExp = self.create_explicit_points_from_halfspace(f)
    return pyattene.orient3d(aExp, bExp, cExp, pExp)

  def orient3dI(self, 
                pImp,
                f: Halfspace) -> int:
    # calcula la orientación del punto implícito p respecto al plano f
    aExp, bExp, cExp = self.create_explicit_points_from_halfspace(f)
    return pyattene.orient3d(aExp, bExp, cExp, pImp)