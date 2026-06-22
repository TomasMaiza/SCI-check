# acá se implementa el módulo que verifica las 3 condiciones iterando sobre cada triángulo
# usar iterator?
from geometry.geometry import AbstractGeometry
from geometry.abstract_structs.point import AbstractPoint
import polytope as pc
from orientresult import OrientResult
from .predicates import AbstractPredicates
from geometry.abstract_structs.halfspace import AbstractHalfspace

class CoverageChecker():
  def __init__(self, geometry: AbstractGeometry, predicates: AbstractPredicates) -> None:
    self._geometry = geometry
    self._predicates = predicates

  def point_out(self, v: AbstractPoint, polytopeSet: dict[pc.Polytope, set[AbstractHalfspace]]):
    # polytopeSet es un diccionario de cada subregion con un conjunto de 
    # los semiespacios que la definen
    for p in polytopeSet.keys():
      counter = 0
      halfspaces = polytopeSet[p]

      for f in halfspaces:
        ori = self._predicates.orient(v, f)
        if (ori == OrientResult.IN):
          counter += 1

      if counter == len(halfspaces):
        return OrientResult.IN
    
    return OrientResult.OUT
