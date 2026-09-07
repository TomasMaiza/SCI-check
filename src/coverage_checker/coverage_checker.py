from .predicates import AbstractPredicates
from geometry import *
from common import *
from .strategy import CoverageCheckStrategy
import logging
import itertools


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

  def implicit_point_in_polytope_TPI(self, 
                                 polytope: Polytope,
                                 f1: AbstractHalfspace,
                                 f2: AbstractHalfspace, 
                                 p: list[AbstractHalfspace]) -> bool:
    ret = True
    if len(p) == 0:
      ret = False
    for fp in p:
      ori = self._predicates.orient_TPI(polytope, f1, f2, fp)
      if ori != IN:
        ret = False
        break
    return ret

  def implicit_point_in_polytope_LPI(self, 
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
      if i != currentpIndex and self.implicit_point_in_polytope_LPI(v1, v2, f, p):
        ret = IN
        break
    return ret

  def plane_plane_poly_out(self, 
                        polytope: Polytope, 
                        f1: AbstractHalfspace, 
                        f2: AbstractHalfspace, 
                        polytopeMap: PolytopeMap, 
                        currentpIndex1: int, 
                        currentpIndex2: int) -> OrientResult:
    if not self._predicates.implicit_point_in_polytope(polytope, f1, f2):
      return IN

    ret = OUT
    for i, p in enumerate(polytopeMap):
      if i not in {currentpIndex1, currentpIndex2} and self.implicit_point_in_polytope_TPI(polytope, f1, f2, p):
        ret = IN
        break

    return ret

  def check_c1(self, 
               polytope: Polytope, 
               polytopeSet: PolytopeMap) -> OrientResult:
    vertices = polytope.get_vertices()
    ret = IN
    for v in vertices:
      v = self._geometry.create_point(tuple(v))
      if self.point_out(v, polytopeSet) == OUT:
        #log.info(f"Vértice OUT: {v}")
        ret = OUT
        break
    return ret

  def check_c2(self, 
               polytope: Polytope, 
               polytopeSet: PolytopeMap) -> OrientResult:
    edges = self._geometry.get_polytope_edges(polytope)
    polytopes = enumerate(polytopeSet)
    for i, p in polytopes:
      for f in p:
        for e in edges:
          if self.edge_plane_out(e[0], e[1], f, polytopeSet, i) == OUT:
            return OUT
    return IN
  
  def check_c3(self, 
               polytope: Polytope, 
               polytopeSet: PolytopeMap) -> OrientResult:
    faces = [(face, i) for i, p in enumerate(polytopeSet) for face in p]
    ret = IN
    for (f1, i), (f2, j) in itertools.combinations(faces, 2):
      if self.plane_plane_poly_out(polytope, f1, f2, polytopeSet, i, j) == OUT:
        ret = OUT
        break  
    return ret

class CoverageChecker(CoverageCheckStrategy):
  def __init__(self, 
               geometry: AbstractGeometry, 
               predicates: AbstractPredicates) -> None:
    self._checker = _CoverageCheckerIntern(geometry, predicates)

  # chequea UN triángulo
  def envelope_check(self, 
                     polytope: Polytope, 
                     polytopeSet: PolytopeMap) -> OrientResult: 
    ret = IN
    if self._checker.check_c1(polytope, polytopeSet) == OUT:
      log.info("Falla C1")
      ret = OUT
    elif self._checker.check_c2(polytope, polytopeSet) == OUT:
      log.info("Falla C2")
      ret = OUT
    elif self._checker.check_c3(polytope, polytopeSet) == OUT:
      log.info("Falla C3")
      ret = OUT
    else:
      log.info("Todo OK")
    return ret
