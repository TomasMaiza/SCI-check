from .predicates import AbstractPredicates
from geometry import *
from common import *
from .strategy import CoverageCheckStrategy
import logging


# Patrón Proxy
class _CoverageCheckerIntern:
  def __init__(self, 
               geometry: AbstractGeometry, 
               predicates: AbstractPredicates) -> None:
    self._geometry = geometry
    self._predicates = predicates

  def point_out(self, 
                v: AbstractPoint, 
                polytopeMap: PolytopeMap) -> OrientResult:
    ret = OUT
    for halfspacesList in polytopeMap:
      isInFlag = True
      if len(halfspacesList) == 0:
        isInFlag = False
      for f in halfspacesList: # con la lista llegan en orden
        ori = self._predicates.orient(v, f)
        if ori == OUT:
          isInFlag = False
          break
      if isInFlag:
        ret = IN
        break
    return ret

  def points_on_same_side(self, 
                          v1: AbstractPoint, 
                          v2: AbstractPoint, 
                          f: AbstractHalfspace) -> bool:
    ori1 = self._predicates.orient(v1, f)
    ori2 = self._predicates.orient(v2, f)
    return ori1 == ori2 or ori1 == ON or ori2 == ON

  def implicit_point_in_polytope(self, 
                                 v1: AbstractPoint, 
                                 v2: AbstractPoint, 
                                 f: AbstractHalfspace, 
                                 p: list[AbstractHalfspace]) -> bool:
    ret = True
    if len(p) == 0:
      ret = False
    for fp in p:
      ori = self._predicates.orient_LPI(v1, v2, f, fp)
      if ori == OUT:
        ret = False
        break
    return ret

  def edge_plane_out(self, 
                    v1: AbstractPoint, 
                    v2: AbstractPoint, 
                    f: AbstractHalfspace, 
                    polytopeMap: PolytopeMap, 
                    currentpIndex: int) -> OrientResult:
    # primero verificamos la posición de los puntos respecto a f
    if self.points_on_same_side(v1, v2, f):
      return IN

    ret = OUT
    for i, p in enumerate(polytopeMap):
      if i != currentpIndex and self.implicit_point_in_polytope(v1, v2, f, p):
        ret = IN
        break
    return ret
  
  '''
  def implicit_point_in_triangle(self, 
                                 triangle: AbstractSimplex, 
                                 f1: AbstractHalfspace, 
                                 f2: AbstractHalfspace) -> bool:
    # determina si un punto (intersección de dos semiespacios) pertenece a un triángulo
    edges = triangle.get_edges()
    r, s = f1.get_points()
    ret = True
    for v1, v2 in edges:
      # queremos calcular la orientación de f1 \\cap f2 respecto a v1v2
      e = self._geometry.create_halfspace((v1, v2))
      ori = self._predicates.orient_LPI(r, s, f2, e)
      if ori != IN:
        ret = False
        break
    return ret'''

  def plane_plane_tri_out(self, 
                        triangle: AbstractSimplex, 
                        f1: AbstractHalfspace, 
                        f2: AbstractHalfspace, 
                        polytopeMap: PolytopeMap, 
                        currentpIndex1: int, 
                        currentpIndex2: int) -> OrientResult:
    if not self._predicates.implicit_point_in_triangle(triangle, f1, f2):
      return IN

    r, s = f1.get_points()
    ret = OUT
    for i, p in enumerate(polytopeMap):
      if i != currentpIndex1 and i != currentpIndex2 and self.implicit_point_in_polytope(r, s, f2, p):
        ret = IN
        break

    return ret

  def check_c1(self, 
               triangle: AbstractSimplex, 
               polytopeSet: PolytopeMap, 
               verticesIndex: VerticesIndex) -> OrientResult:
    vertices = triangle.get_vertices()
    ret = IN
    for v in vertices:
      if not verticesIndex[v] and self.point_out(v, polytopeSet) == OUT:
        ret = OUT
        break
      verticesIndex[v] = True # pisamos el valor si ya era True y sino lo marcamos por primera vez
    return ret

  def check_c2(self, 
               triangle: AbstractSimplex, 
               polytopeSet: PolytopeMap, 
               edgesIndex: EdgesIndex) -> OrientResult:
    allEdges = triangle.get_all_edges()
    edges, invEdges = allEdges
    polytopes = enumerate(polytopeSet)
    for i, p in polytopes:
      for f in p:
        for e in edges:
          if not edgesIndex[e] and self.edge_plane_out(e[0], e[1], f, polytopeSet, i) == OUT:
            return OUT
    for e in edges + invEdges:
      edgesIndex[e] = True
    return IN
  
  def check_c3(self, 
               triangle: AbstractSimplex, 
               polytopeSet: PolytopeMap) -> OrientResult:
    polytopes = list(enumerate(polytopeSet))
    for i, pi in polytopes:
      for j, pj in polytopes[i:]:
        for fi in pi:
          for fj in pj:
            if self.plane_plane_tri_out(triangle, fi, fj, polytopeSet, i, j) == OUT:
              return OUT
    return IN

class CoverageChecker(CoverageCheckStrategy):
  def __init__(self, 
               geometry: AbstractGeometry, 
               predicates: AbstractPredicates) -> None:
    self._checker = _CoverageCheckerIntern(geometry, predicates)

  # chequea UN triángulo
  def envelope_check(self, 
                     triangle: AbstractSimplex, 
                     polytopeSet: PolytopeMap, 
                     verticesIndex: VerticesIndex, 
                     edgesIndex: EdgesIndex) -> OrientResult: 
    ret = IN
    if self._checker.check_c1(triangle, polytopeSet, verticesIndex) == OUT:
      log.info("Falla C1")
      ret = OUT
    elif self._checker.check_c2(triangle, polytopeSet, edgesIndex) == OUT:
      log.info("Falla C2")
      ret = OUT
    elif self._checker.check_c3(triangle, polytopeSet) == OUT:
      log.info("Falla C3")
      ret = OUT
    else:
      log.info("Todo OK")
    return ret
