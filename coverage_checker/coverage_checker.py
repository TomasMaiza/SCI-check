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
        if ori != OUT: # puede ser ON o OUT. REVISAR QUE DEBERÍA PASAR EN CASO DE ON
          isInFlag = False
          break

      if isInFlag:
        ret = IN
        break
    
    return ret

  def edge_plane_out(self, v1: AbstractPoint, v2: AbstractPoint, f: AbstractHalfspace, polytopeMap: PolytopeMap, currentpIndex: int) -> OrientResult:
    ret = OUT
    
    # primero verificamos la posición de los puntos respecto a f
    ori1 = self._predicates.orient(v1, f)
    ori2 = self._predicates.orient(v2, f)
    if ori1 == ori2 or ori1 == ON or ori2 == ON:
      return IN
    
    for i, p in enumerate(polytopeMap):
      if i == currentpIndex:
        continue
      isInFlag = True
      for fp in p:
        ori = self._predicates.orient_LPI(v1, v2, f, fp)
        if ori != IN: # puede ser ON o OUT
          isInFlag = False
          break
      if isInFlag:
        ret = IN
        break

    return ret
  
  # chequea UN triángulo
  def envelope_check(self, triangle: AbstractSimplex, polytopeSet: PolytopeMap, verticesIndex: VerticesIndex) -> OrientResult: 
    vertices = set(triangle.get_vertices())
    
    ret = IN
    if self.check_c1(vertices, polytopeSet, verticesIndex) == OUT:
      ret = OUT
    if self.check_c2(triangle, polytopeSet) == OUT:
      ret = OUT
    # self.check_c3()
    return ret

  def check_c1(self, vertices: set[AbstractPoint], polytopeSet: PolytopeMap, verticesIndex: VerticesIndex) -> OrientResult:
    ret = IN
    for v in vertices:
      if not verticesIndex[v] and self.point_out(v, polytopeSet) == OUT:
        ret = OUT
        break
      verticesIndex[v] = True # pisamos el valor si ya era True y sino lo marcamos por primera vez
    return ret

  # en check_c2 ver cómo manejar lo del PS\P
  # analizar si se están verificando cosas dos veces
  def check_c2(self, triangle: AbstractSimplex, polytopeSet: PolytopeMap) -> OrientResult:
    edges = triangle.get_edges() # ACÁ TAMBIÉN SE PODRÍA OPTIMIZAR PARA NO REPETIR ARISTAS

    for i, p in enumerate(polytopeSet):
      for f in p:
        for e in edges:
          if self.edge_plane_out(e[0], e[1], f, polytopeSet, i) == OUT:
            return OUT
      
    return IN
