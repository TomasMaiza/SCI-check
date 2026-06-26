# acá se implementa el módulo que verifica las 3 condiciones iterando sobre cada triángulo
# usar iterator?
from geometry.geometry import AbstractGeometry
from geometry.abstract_structs.point import AbstractPoint
import polytope as pc
from .predicates import AbstractPredicates
from geometry.abstract_structs.halfspace import AbstractHalfspace
from geometry.abstract_structs.simplex import AbstractSimplex
from common.enums import OrientResult
from common.types import PolytopeMap, VerticesIndex

IN = OrientResult.IN
OUT = OrientResult.OUT
ON = OrientResult.ON

class CoverageChecker():
  def __init__(self, geometry: AbstractGeometry, predicates: AbstractPredicates) -> None:
    self._geometry = geometry
    self._predicates = predicates

  def point_out(self, v: AbstractPoint, polytopeMap: PolytopeMap) -> OrientResult:
    ret = OUT
    
    for halfspacesList in polytopeMap:
      isInFlag = True
      for f in halfspacesList: # con la lista llegan en orden
        ori = self._predicates.orient(v, f)
        if (ori == OUT):
          isInFlag = False
          break

      if isInFlag:
        ret = IN
        break
    
    return ret

  def edge_plane_out():
    pass
  
  # chequea UN triángulo
  def envelope_check(self, triangle: AbstractSimplex, polytopeSet: PolytopeMap, verticesIndex: VerticesIndex) -> OrientResult: 
    vertices = set(triangle.get_vertices())
    
    ret = IN
    if self.check_c1(vertices, polytopeSet, verticesIndex) == OUT:
      ret = OUT
    # check_c2()
    # check_c3()
    return ret

  def check_c1(self, vertices: set[AbstractPoint], polytopeSet: PolytopeMap, verticesIndex: VerticesIndex) -> OrientResult:
    ret = IN
    for v in vertices:
      if not verticesIndex[v] and self.point_out(v, polytopeSet) == OUT:
        ret = OUT
        break
      verticesIndex[v] = True # pisamos el valor si ya era True y sino lo marcamos por primera vez
    return ret

