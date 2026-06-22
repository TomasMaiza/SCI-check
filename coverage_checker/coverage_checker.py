# acá se implementa el módulo que verifica las 3 condiciones iterando sobre cada triángulo
# usar iterator?
from geometry.geometry import AbstractGeometry
from geometry.abstract_structs.point import AbstractPoint
import polytope as pc
from orientresult import OrientResult
from .predicates import AbstractPredicates
from geometry.abstract_structs.halfspace import AbstractHalfspace
from geometry.abstract_structs.simplex import AbstractSimplex

IN = OrientResult.IN
OUT = OrientResult.OUT

type PolytopeMap = dict[pc.Polytope, set[AbstractHalfspace]]
# diccionario de cada subregion con un conjunto de los semiespacios que la definen

class CoverageChecker():
  def __init__(self, geometry: AbstractGeometry, predicates: AbstractPredicates) -> None:
    self._geometry = geometry
    self._predicates = predicates

  def point_out(self, v: AbstractPoint, polytopeSet: PolytopeMap):
    # polytopeSet es un diccionario de cada subregion con un conjunto de 
    # los semiespacios que la definen
    for p in polytopeSet.keys():
      counter = 0
      halfspaces = polytopeSet[p]

      for f in halfspaces:
        ori = self._predicates.orient(v, f)
        if (ori == IN):
          counter += 1

      if counter == len(halfspaces):
        return IN
    
    return OUT
  
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

