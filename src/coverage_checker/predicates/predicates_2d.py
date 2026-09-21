from common import OrientResult, IN, ON, OUT
from geometry.structs_2d import *
from geometry import Polytope, Geometry2d, Halfspace
from .predicates import AbstractPredicates
from bindings import AtteneAdapter2D

class Predicates2d(AbstractPredicates):
  # clase para implementar los predicados en 2d

  def __init__(self):
    self._adapter = AtteneAdapter2D()

  def orient(self, v: Point2D, f: Halfspace) -> OrientResult: # retorna IN, OUT, ON
    # calcula la orientación de v respecto a f
    ori = self._adapter.orient2d_EEE(v, f)

    if ori == 1:
      ret = OrientResult.IN
    elif ori == 0:
      ret = OrientResult.ON
    else:
      ret = OrientResult.OUT
    return ret

  def orient_LPI(self, 
                 r: Point2D, 
                 s: Point2D, 
                 f1: Halfspace, 
                 ref: Halfspace) -> OrientResult:
    # queremos calcular la orientación de f1 \cap rs respecto a ref
    pImp = self._adapter.create_implicit_point_ssi(r, s, f1) # Punto implícito: intersección de rs con f1
    ori = self._adapter.orient2d_IEE(pImp, ref)

    if ori == 1:
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
                 ref: Halfspace) -> OrientResult: # retorna IN, OUT, ON
    r, s = f1.get_points()
    return self.orient_LPI(r, s, f2, ref)

  def implicit_point_in_polytope(self, 
                                 polytope: Polytope, 
                                 f1: Halfspace, 
                                 f2: Halfspace) -> bool: 
    # determina si un punto (intersección de dos semiespacios) pertenece a un politopo
    #edges = polytope.get_edges()
    r, s = f1.get_points()
    hs = polytope.get_halfspaces()
    ret = True
    for f in hs:
      # queremos calcular la orientación de f1 \cap f2 respecto a v1v2
      ori = self.orient_LPI(r, s, f2, f)
      if ori != IN:
        ret = False
        break
    return ret

    # VER ACÁ LO DE LOS CENTROIDES SI LAS ARISTAS NO ESTÁN ORDENADAS / PARA NO ORDENARLAS