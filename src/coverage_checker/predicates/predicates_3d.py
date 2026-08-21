from common import OrientResult, IN, ON, OUT
from geometry.structs_3d import *
from .predicates import AbstractPredicates
from shewchuk import orientation
from .. import pyattene

class Predicates3d(AbstractPredicates):
  # clase para implementar los predicados en 3d

  def orient(self, v: Point3D, f: Halfspace3D) -> OrientResult: # retorna IN, OUT, ON
    a, b, c = f.get_points()
    vExp = pyattene.ExplicitPoint3D(v.x, v.y, v.z)
    aExp = pyattene.ExplicitPoint3D(a.x, a.y, a.z)
    bExp = pyattene.ExplicitPoint3D(b.x, b.y, b.z)
    cExp = pyattene.ExplicitPoint3D(c.x, c.y, c.z)

    ori = pyattene.orient3d(vExp, aExp, bExp, cExp)

    if ori == -1: # REVISAR ORIENTACIÓN DEL HALFSPACE 3D
      ret = OrientResult.IN
    elif ori == 0:
      ret = OrientResult.ON
    else:
      ret = OrientResult.OUT
    return ret
    
  def orient_LPI(self, r: Point3D, s: Point3D, f1: Halfspace3D, f2: Halfspace3D) -> OrientResult: # retorna IN, OUT, ON
    t, u, v = f1.get_points()
    a, b, c = f2.get_points()
    # queremos calcular la orientación de f1 \cap rs respecto a f2
    
    rExp = pyattene.ExplicitPoint3D(r.x, r.y, r.z)
    sExp = pyattene.ExplicitPoint3D(s.x, s.y, s.z)

    tExp = pyattene.ExplicitPoint3D(t.x, t.y, t.z)
    uExp = pyattene.ExplicitPoint3D(u.x, u.y, u.z)
    vExp = pyattene.ExplicitPoint3D(v.x, v.y, v.z)

    aExp = pyattene.ExplicitPoint3D(a.x, a.y, a.z)
    bExp = pyattene.ExplicitPoint3D(b.x, b.y, b.z)
    cExp = pyattene.ExplicitPoint3D(c.x, c.y, c.z)

    # Punto implícito: intersección de rs con tu
    pImp = pyattene.ImplicitPoint3D_LPI(rExp, sExp, tExp, uExp, vExp)

    ori = pyattene.orient3d(pImp, aExp, bExp, cExp)

    if ori == -1:
      ret = OrientResult.IN
    elif ori == 0:
      ret = OrientResult.ON
    else:
      ret = OrientResult.OUT
    return ret

  def orient_TPI_halfspaces(self, 
                            f: Halfspace3D, 
                            f1: Halfspace3D, 
                            f2: Halfspace3D, 
                            ref: Halfspace3D) -> OrientResult: # retorna IN, OUT, ON
    t, u, v = f1.get_points()
    a, b, c = f2.get_points()
    r, s, q = ref.get_points()
    v1, v2, v3 = f.get_points()

    tExp = pyattene.ExplicitPoint3D(t.x, t.y, t.z)
    uExp = pyattene.ExplicitPoint3D(u.x, u.y, u.z)
    vExp = pyattene.ExplicitPoint3D(v.x, v.y, v.z)

    aExp = pyattene.ExplicitPoint3D(a.x, a.y, a.z)
    bExp = pyattene.ExplicitPoint3D(b.x, b.y, b.z)
    cExp = pyattene.ExplicitPoint3D(c.x, c.y, c.z)

    rExp = pyattene.ExplicitPoint3D(r.x, r.y, r.z)
    sExp = pyattene.ExplicitPoint3D(s.x, s.y, s.z)
    qExp = pyattene.ExplicitPoint3D(q.x, q.y, q.z)

    v1Exp = pyattene.ExplicitPoint3D(v1.x, v1.y, v1.z)
    v2Exp = pyattene.ExplicitPoint3D(v2.x, v2.y, v2.z)
    v3Exp = pyattene.ExplicitPoint3D(v3.x, v3.y, v3.z)

    # Punto implícito: intersección del triángulo con f1 y f2
    pImp = pyattene.ImplicitPoint3D_TPI(v1Exp, v2Exp, v3Exp,
                                        tExp, uExp, vExp,
                                        aExp, bExp, cExp)

    ori = pyattene.orient3d(pImp, rExp, sExp, qExp)

    if ori == -1:
      ret = OrientResult.IN
    elif ori == 0:
      ret = OrientResult.ON
    else:
      ret = OrientResult.OUT
    return ret

  def orient_TPI(self, 
                 triangle: Triangle3D, 
                 f1: Halfspace3D, 
                 f2: Halfspace3D, 
                 ref: Halfspace3D) -> OrientResult:
    vertices = triangle.get_vertices()
    f = Halfspace3D(points = vertices)
    return self.orient_TPI_halfspaces(f, f1, f2, ref)

  def implicit_point_in_triangle(self, 
                                 triangle: Triangle3D, 
                                 f1: Halfspace3D, 
                                 f2: Halfspace3D) -> bool: 
    # retorna si un punto implícito está en el plano de un triángulo
    r, s, t = f1.get_points()
    u, v, w = f2.get_points()
    a, b, c = triangle.get_vertices()

    rExp = pyattene.ExplicitPoint3D(r.x, r.y, r.z)
    sExp = pyattene.ExplicitPoint3D(s.x, s.y, s.z)
    tExp = pyattene.ExplicitPoint3D(t.x, t.y, t.z)
    
    uExp = pyattene.ExplicitPoint3D(u.x, u.y, u.z)
    vExp = pyattene.ExplicitPoint3D(v.x, v.y, v.z)
    wExp = pyattene.ExplicitPoint3D(w.x, w.y, w.z)

    aExp = pyattene.ExplicitPoint3D(a.x, a.y, a.z)
    bExp = pyattene.ExplicitPoint3D(b.x, b.y, b.z)
    cExp = pyattene.ExplicitPoint3D(c.x, c.y, c.z)

    pImp = pyattene.ImplicitPoint3D_TPI(aExp, bExp, cExp, # está bien esto?
                                        rExp, sExp, tExp,
                                        uExp, vExp, wExp)
    return pyattene.pointInTriangle(pImp, aExp, bExp, cExp)