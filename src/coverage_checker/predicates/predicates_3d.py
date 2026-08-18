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

  def orient_TPI(self) -> OrientResult: # retorna IN, OUT, ON
    pass