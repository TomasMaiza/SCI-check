from common import OrientResult, IN, ON, OUT, Point
from geometry.structs_3d import *
from geometry import Polytope, Geometry3d, Halfspace
from .predicates import AbstractPredicates
from fractions import Fraction
from bindings import AtteneAdapter3D

class Predicates3d(AbstractPredicates):
  # clase para implementar los predicados en 3d

  def __init__(self):
    self._adapter = AtteneAdapter3D()

  def orient(self, v: Point3D, f: Halfspace) -> OrientResult: # retorna IN, OUT, ON
    ori = self._adapter.orient3dE(v.get_point(), f)

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
                 f1: Halfspace, 
                 ref: Halfspace) -> OrientResult: # retorna IN, OUT, ON
    # queremos calcular la orientación de f1 \cap rs respecto a ref
    pImp = self._adapter.create_implicit_point_lpi(r.get_point(), s.get_point(), f1) # Punto implícito: intersección de rs con f1
    ori = self._adapter.orient3dI(pImp, ref)

    if ori == -1:
      ret = OrientResult.IN
    elif ori == 0:
      ret = OrientResult.ON
    else:
      ret = OrientResult.OUT
    return ret

  def orient_TPI_halfspaces(self, 
                            f: Halfspace, 
                            f1: Halfspace, 
                            f2: Halfspace, 
                            ref: Halfspace) -> OrientResult: # retorna IN, OUT, ON
    # calcula la orientación del punto intersección de f, f1 y f2 respecto a ref
    pImp = self._adapter.create_implicit_point_tpi(f, f1, f2) # Punto implícito: intersección del plano f con f1 y f2
    ori = self._adapter.orient3dI(pImp, ref)

    if ori == -1:
      ret = OrientResult.IN
    elif ori == 0:
      ret = OrientResult.ON
    else:
      ret = OrientResult.OUT
    return ret

  def orient_TPI(self, 
                 polytope: Polytope, 
                 f1: Halfspace, 
                 f2: Halfspace, 
                 ref: Halfspace) -> OrientResult:
    # predicado para la cara de un politopo
    vertices = polytope.get_vertices()
    if len(vertices) < 3:
      return OUT
    
    a = (float(vertices[0][0]), float(vertices[0][1]), float(vertices[0][2]))
    b = (float(vertices[1][0]), float(vertices[1][1]), float(vertices[1][2]))
    c = (float(vertices[2][0]), float(vertices[2][1]), float(vertices[2][2]))
    
    f = Halfspace(points = [a, b, c])
    return self.orient_TPI_halfspaces(f, f1, f2, ref)

  def _parallel_halfspaces(self,
                           f1: Halfspace,
                           f2: Halfspace,
                           f3: Halfspace) -> bool:
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
                          f: Halfspace, 
                          f1: Halfspace, 
                          f2: Halfspace, 
                          refHalfspace: Halfspace, 
                          refPoint: Point) -> bool:
    # calcula si el punto implícito de intersección de tres planos tiene la misma orientación
    # que un punto interno refPoint
    oriImpPoint = self.orient_TPI_halfspaces(f, f1, f2, refHalfspace)
    oriRefPoint = self.orient(refPoint, refHalfspace)
    return oriImpPoint == oriRefPoint # qué pasa con los ON?

  def _get_centroid(self, a: Point, b: Point, c: Point) -> Point:
    # retorna un punto interno del politopo
    # a futuro ver si hacer una función get_intern_point en polytope (get_centroid) para reutilizar
    cx = (a[0] + b[1] + c[2]) / 3.0
    cy = (a[0] + b[1] + c[2]) / 3.0
    cz = (a[0] + b[1] + c[2]) / 3.0
    return (cx, cy, cz)

  def implicit_point_in_polytope(self, 
                                      polytope: Polytope, 
                                      f1: Halfspace, 
                                      f2: Halfspace) -> bool: 
    # retorna si un punto implícito está en el plano de la CARA de un politopo
    vertices = polytope.get_vertices()
    if len(vertices) < 3:
      return False
    
    a = (float(vertices[0][0]), float(vertices[0][1]), float(vertices[0][2]))
    b = (float(vertices[1][0]), float(vertices[1][1]), float(vertices[1][2]))
    c = (float(vertices[2][0]), float(vertices[2][1]), float(vertices[2][2]))
    
    f = Halfspace(points = [a, b, c])
    if self._parallel_halfspaces(f1, f2, f):
      return False

    centroid = self._get_centroid(a, b, c)
    # centroide del triángulo abc
    # es un punto interno del politopo para tomar de referencia

    nx, ny, nz = self._calculate_normal(a, b, c)
    edges = polytope.get_edges()
    for e in edges:
      v1 = (float(e[0][0]), float(e[0][1]), float(e[0][2]))
      v2 = (float(e[1][0]), float(e[1][1]), float(e[1][2]))
      q = (v1[0] + nx, v1[1] + ny, v1[2] + nz)
      ref = Halfspace(points = [v1, v2, q])
      if not self._point_on_same_side(f, f1, f2, ref, centroid):
        return False
    return True

  def implicit_point_in_polytope_3d(self, 
                                     polytope: Polytope, 
                                     f1: Halfspace, 
                                     f2: Halfspace,
                                     f3: Halfspace) -> bool:
    # intersección de punto implícito producto de 3 semiespacios con un politopo 3d
    vertices = polytope.get_vertices()
    if len(vertices) < 3:
      return False # o true?
    a = (float(vertices[0][0]), float(vertices[0][1]), float(vertices[0][2]))
    b = (float(vertices[1][0]), float(vertices[1][1]), float(vertices[1][2]))
    c = (float(vertices[2][0]), float(vertices[2][1]), float(vertices[2][2]))
    centroid = self._get_centroid(a, b, c)
    
    ret = True
    faces = polytope.get_halfspaces()
    for ref in faces:
      if not self._point_on_same_side(f1, f2, f3, ref, centroid):
        ret = False
        break
    return ret