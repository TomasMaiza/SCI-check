from common import OrientResult, IN, ON, OUT
from geometry.structs_3d import *
from geometry import Polytope, Geometry3d
from .predicates import AbstractPredicates
from fractions import Fraction
from .. import pyattene

class Predicates3d(AbstractPredicates):
  # clase para implementar los predicados en 3d

  def orient(self, v: Point3D, f: Halfspace3D) -> OrientResult: # retorna IN, OUT, ON
    a, b, c = f.get_points()
    vExp = pyattene.ExplicitPoint3D(v.x, v.y, v.z)
    aExp = pyattene.ExplicitPoint3D(a.x, a.y, a.z)
    bExp = pyattene.ExplicitPoint3D(b.x, b.y, b.z)
    cExp = pyattene.ExplicitPoint3D(c.x, c.y, c.z)

    ori = pyattene.orient3d(aExp, bExp, cExp, vExp)

    if ori == -1: # REVISAR ORIENTACIÓN DEL HALFSPACE 3D
      ret = OrientResult.IN
    elif ori == 0:
      ret = OrientResult.ON
    else:
      ret = OrientResult.OUT
    return ret
    
  def orient_LPI(self, 
                 r: Point3D, 
                 s: Point3D, 
                 f1: Halfspace3D, 
                 ref: Halfspace3D) -> OrientResult: # retorna IN, OUT, ON
    t, u, v = f1.get_points()
    a, b, c = ref.get_points()
    # queremos calcular la orientación de f1 \cap rs respecto a ref
    
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
                 polytope: Polytope, 
                 f1: Halfspace3D, 
                 f2: Halfspace3D, 
                 ref: Halfspace3D) -> OrientResult:
    # predicado para la cara de un politopo
    vertices = polytope.get_vertices()
    if len(vertices) < 3:
      return OUT
    
    a = Point3D(x=float(vertices[0][0]), y=float(vertices[0][1]), z=float(vertices[0][2]))
    b = Point3D(x=float(vertices[1][0]), y=float(vertices[1][1]), z=float(vertices[1][2]))
    c = Point3D(x=float(vertices[2][0]), y=float(vertices[2][1]), z=float(vertices[2][2]))
    
    f = Halfspace3D(points = (a, b, c))
    return self.orient_TPI_halfspaces(f, f1, f2, ref)

  def _parallel_halfspaces(self,
                           f1: Halfspace3D,
                           f2: Halfspace3D,
                           f3: Halfspace3D) -> bool:
    n1 = f1.get_normal()
    n2 = f2.get_normal()
    n3 = f3.get_normal()
    det = n1[0]*(n2[1]*n3[2] - n2[2]*n3[1]) - n1[1]*(n2[0]*n3[2] - n2[2]*n3[0]) + n1[2]*(n2[0]*n3[1] - n2[1]*n3[0])
    return det == 0

  def _calculate_normal(self, a: Point3D, b: Point3D, c: Point3D) -> tuple[float, float, float]:
    # Calcula el vector normal a la cara dados 3 vértices no colineales. 
    ab_x = b.x - a.x
    ab_y = b.y - a.y
    ab_z = b.z - a.z

    ac_x = c.x - a.x
    ac_y = c.y - a.y
    ac_z = c.z - a.z

    nx = (ab_y * ac_z) - (ab_z * ac_y)
    ny = (ab_z * ac_x) - (ab_x * ac_z)
    nz = (ab_x * ac_y) - (ab_y * ac_x)
    
    return nx, ny, nz

  def _point_on_same_side(self, 
                          f: Halfspace3D, 
                          f1: Halfspace3D, 
                          f2: Halfspace3D, 
                          refHalfspace: Halfspace3D, 
                          refPoint: Point3D) -> bool:
    # calcula si el punto implícito de intersección de tres planos tiene la misma orientación
    # que un punto interno refPoint
    oriImpPoint = self.orient_TPI_halfspaces(f, f1, f2, refHalfspace)
    oriRefPoint = self.orient(refPoint, refHalfspace)
    return oriImpPoint == oriRefPoint # qué pasa con los ON?

  def _get_centroid(self, a: Point3D, b: Point3D, c: Point3D) -> Point3D:
    # retorna un punto interno del politopo
    # a futuro ver si hacer una función get_intern_point o algo así para reutilizar
    cx = (a.x + b.x + c.x) / 3.0
    cy = (a.y + b.y + c.y) / 3.0
    cz = (a.z + b.z + c.z) / 3.0
    return Point3D(cx, cy, cz)

  def implicit_point_in_polytope_face(self, 
                                      polytope: Polytope, 
                                      f1: Halfspace3D, 
                                      f2: Halfspace3D) -> bool: 
    # retorna si un punto implícito está en el plano de la cara de un politopo
    vertices = polytope.get_vertices()
    if len(vertices) < 3:
      return False
    
    a = Point3D(x=float(vertices[0][0]), y=float(vertices[0][1]), z=float(vertices[0][2]))
    b = Point3D(x=float(vertices[1][0]), y=float(vertices[1][1]), z=float(vertices[1][2]))
    c = Point3D(x=float(vertices[2][0]), y=float(vertices[2][1]), z=float(vertices[2][2]))
    
    f = Halfspace3D(points = (a, b, c))
    if self._parallel_halfspaces(f1, f2, f):
      return False

    centroid = self._get_centroid(a, b, c)
    # centroide del triángulo abc
    # es un punto interno del politopo para tomar de referencia

    nx, ny, nz = self._calculate_normal(a, b, c)
    edges = polytope.get_edges()
    for e in edges:
      v1 = Point3D(float(e[0][0]), float(e[0][1]), float(e[0][2]))
      v2 = Point3D(float(e[1][0]), float(e[1][1]), float(e[1][2]))
      q = Point3D(v1.x + nx, v1.y + ny, v1.z + nz)
      ref = Halfspace3D(points = (v1, v2, q))
      if not self._point_on_same_side(f, f1, f2, ref, centroid):
        return False
    return True

  def implicit_point_in_polytope_3d(self, 
                                     polytope: Polytope, 
                                     f1: Halfspace3D, 
                                     f2: Halfspace3D,
                                     f3: Halfspace3D) -> bool:
    # intersección de punto implícito producto de 3 semiespacios con un politopo 3d
    ret = True
    faces = polytope.get_faces()
    for p in faces:
      vertices = p.get_vertices() # FUNCIÓN get_plane EN POLYTOPE? EN HALFSPACE?
      if len(vertices) < 3:
        return False # o true?
      a = Point3D(x=float(vertices[0][0]), y=float(vertices[0][1]), z=float(vertices[0][2]))
      b = Point3D(x=float(vertices[1][0]), y=float(vertices[1][1]), z=float(vertices[1][2]))
      c = Point3D(x=float(vertices[2][0]), y=float(vertices[2][1]), z=float(vertices[2][2]))
      ref = Halfspace3D(points = (a, b, c))
      centroid = self._get_centroid(a, b, c)
      ori = self._point_on_same_side(f1, f2, f3, ref, centroid)
      if ori == OUT:
        ret = False
        break
    return ret