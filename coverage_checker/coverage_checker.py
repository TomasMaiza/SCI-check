# acá se implementa el módulo que verifica las 3 condiciones iterando sobre cada triángulo
# usar iterator?
from geometry.geometry import AbstractGeometry
from geometry.abstract_structs.point import AbstractPoint
import polytope as pc
from .predicates import AbstractPredicates
from geometry.abstract_structs.halfspace import AbstractHalfspace
from geometry.abstract_structs.simplex import AbstractSimplex
from common.enums import OrientResult
from common.types import PolytopeMap, VerticesIndex, EdgesIndex

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
        if ori != IN: # puede ser ON o OUT. REVISAR QUE DEBERÍA PASAR EN CASO DE ON
          isInFlag = False
          break

      if isInFlag:
        ret = IN
        break
    
    return ret

  def edge_edge_out(self, v1: AbstractPoint, v2: AbstractPoint, f: AbstractHalfspace, polytopeMap: PolytopeMap, currentpIndex: int) -> OrientResult:
    # primero verificamos la posición de los puntos respecto a f
    ori1 = self._predicates.orient(v1, f)
    ori2 = self._predicates.orient(v2, f)
    if ori1 == ori2 or ori1 == ON or ori2 == ON:
      return IN
    
    ret = OUT
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
  
  def edge_edge_tri_out(self, triangle: AbstractSimplex, f1: AbstractHalfspace, f2: AbstractHalfspace, polytopeMap: PolytopeMap, currentpIndex1: int, currentpIndex2: int) -> OrientResult: 
    edges = triangle.get_edges()
    r, s = f1.get_points()
    for v1, v2 in edges:
      # orient_LPI(r, s, f1, f2)
      # calcula la orientación de f1 \cap rs respecto a f2
      # queremos calcular la orientación de f1 \cap f2 respecto a v1v2
      e = self._geometry.create_halfspace(v1, v2)
      ori = self._predicates.orient_LPI(r, s, f2, e)
      if ori != IN:
        return IN

    ret = OUT
    for i, p in enumerate(polytopeMap):
      if i == currentpIndex1 or i == currentpIndex2:
        continue
      isInFlag = True
      for fp in p:
        ori = self._predicates.orient_LPI(r, s, f2, fp)
        if ori != IN: # puede ser ON o OUT
          isInFlag = False
          break
      if isInFlag:
        ret = IN
        break

    return ret

  
  # chequea UN triángulo
  def envelope_check(self, triangle: AbstractSimplex, polytopeSet: PolytopeMap, verticesIndex: VerticesIndex, edgesIndex: EdgesIndex) -> OrientResult: 
    vertices = set(triangle.get_vertices())
    
    ret = IN
    if self.check_c1(vertices, polytopeSet, verticesIndex) == OUT:
      ret = OUT
    if self.check_c2(triangle, polytopeSet, edgesIndex) == OUT:
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

  def check_c2(self, triangle: AbstractSimplex, polytopeSet: PolytopeMap, edgesIndex: EdgesIndex) -> OrientResult:
    allEdges = triangle.get_all_edges()
    edges, invEdges = allEdges
    for i, p in enumerate(polytopeSet):
      for f in p:
        for e in edges:
          if not edgesIndex[e] and self.edge_edge_out(e[0], e[1], f, polytopeSet, i) == OUT:
            return OUT
    for e in allEdges:
      edgesIndex[e] = True
    return IN
  
  def check_c3(self):
    pass
