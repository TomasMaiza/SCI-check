from common import OrientResult, IN, ON, OUT, Point
from geometry import Polytope, Halfspace
from .predicates import AbstractPredicates
from fractions import Fraction
from bindings import AtteneAdapter3D
import numpy as np

class Predicates3d(AbstractPredicates):
  # clase para implementar los predicados en 3d

  def __init__(self):
    self._adapter = AtteneAdapter3D()

  def orient(self, v: Point, f: Halfspace) -> OrientResult: # retorna IN, OUT, ON
    ori = self._adapter.orient3dE(v, f)

    if ori == -1: # REVISAR ORIENTACIÓN DEL HALFSPACE 3D
      ret = OrientResult.IN
    elif ori == 0:
      ret = OrientResult.ON
    else:
      ret = OrientResult.OUT
    return ret
    
  def orient_LPI(self, 
                 r: Point, 
                 s: Point, 
                 f1: Halfspace, 
                 ref: Halfspace) -> OrientResult: # retorna IN, OUT, ON
    # queremos calcular la orientación de f1 \cap rs respecto a ref
    pImp = self._adapter.create_implicit_point_lpi(r, s, f1) # Punto implícito: intersección de rs con f1
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
    return oriImpPoint == oriRefPoint

  def implicit_point_in_polytope(self, 
                                      polytope: Polytope, 
                                      f1: Halfspace, 
                                      f2: Halfspace) -> bool: 
    # retorna si un punto implícito está en el plano de la CARA de un politopo
    # lo usa el checker 2d, por eso hago get_edges y no get_boundaries
    vertices = polytope.get_vertices()
    if len(vertices) < 3:
      return False
    
    facePoints = [tuple(float(c) for c in v) for v in vertices]
    f = Halfspace(points=facePoints)

    centroid = polytope.get_centroid() # es un punto interno del politopo para tomar de referencia
    normal = f.get_normal() 
    edges = polytope.get_edges() # en nd, esto cambia a get_boundaries()
    for e in edges:
      ref_points = [tuple(float(c) for c in v) for v in e]
      v_base = np.array(e[0])
      q_array = v_base + normal
      q = tuple(float(c) for c in q_array)
      ref_points.append(q)
      ref = Halfspace(points=ref_points)
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
    centroid = polytope.get_centroid()
    
    ret = True
    faces = polytope.get_halfspaces()
    for ref in faces:
      if not self._point_on_same_side(f1, f2, f3, ref, centroid):
        ret = False
        break
    return ret