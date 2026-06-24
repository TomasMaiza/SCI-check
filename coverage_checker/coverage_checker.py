# acá se implementa el módulo que verifica las 3 condiciones iterando sobre cada triángulo
# usar iterator?
from geometry.geometry import AbstractGeometry
from geometry.abstract_structs.point import AbstractPoint
import polytope as pc
from .predicates import AbstractPredicates
from geometry.abstract_structs.halfspace import AbstractHalfspace
from geometry.abstract_structs.simplex import AbstractSimplex
from common.enums import OrientResult
from common.types import PolytopeMap

IN = OrientResult.IN
OUT = OrientResult.OUT

class CoverageChecker():
  def __init__(self, geometry: AbstractGeometry, predicates: AbstractPredicates) -> None:
    self._geometry = geometry
    self._predicates = predicates

  def point_out(self, v: AbstractPoint, polytopeMap: PolytopeMap):
    ret = OUT
    
    for halfspacesSet in polytopeMap:
      counter = 0

      for f in halfspacesSet:
        ori = self._predicates.orient(v, f)
        if (ori == IN):
          counter += 1

      if counter == len(halfspacesSet):
        ret = IN
        break
    
    return ret
  
  def edge_plane_out():
    pass
  
  def envelope_check(self, triangle: AbstractSimplex, polytopeSet: PolytopeMap): # chequea UN triángulo
    vertices = set(triangle.get_vertices())
    
    if self.check_c1(vertices, polytopeSet) == OUT:
      ret = OUT
    # check_c2()
    # check_c3()
    return ret

  def check_c1(self, vertices: set[AbstractPoint], polytopeSet: PolytopeMap):
    ret = IN
    for v in vertices:
      if self.point_out(v, polytopeSet) == OUT:
        ret = OUT
        break
    return ret

