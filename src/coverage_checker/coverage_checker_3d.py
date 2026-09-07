from .predicates import AbstractPredicates
from geometry import *
from geometry.structs_3d import *
from common import *
from .strategy import CoverageCheckStrategy
from .coverage_checker import CoverageChecker
import logging
import itertools

# Patrón Decorator
class CoverageChecker3D(CoverageChecker):
  def __init__(self, 
               geometry: AbstractGeometry, 
               predicates: AbstractPredicates) -> None:
    self._checker = CoverageChecker(geometry, predicates)
    self._geometry = geometry
    self._predicates = predicates

  def implicit_point_in_polytope_TPI(self,
                                        polytope: Polytope, 
                                        f1: AbstractHalfspace, 
                                        f2: AbstractHalfspace, 
                                        f3: AbstractHalfspace):
    ret = True
    triangles = polytope.get_faces()
    for t in triangles:
      vertices = t.get_vertices()
      f = Halfspace3D(points = vertices)
      ori = self._predicates.orient_TPI_halfspaces(f1, f2, f3, f)
      if ori == OUT:
        ret = False
        break
    return ret

  def implicit_point_in_polytope_TPI(self, 
                                     f1: AbstractHalfspace,
                                     f2: AbstractHalfspace, 
                                     f3: AbstractHalfspace, 
                                     p: list[AbstractHalfspace]) -> bool:
    ret = True
    if len(p) == 0:
      ret = False
    for fp in p:
      ori = self._predicates.orient_TPI_halfspaces(f1, f2, f3, fp)
      if ori == OUT:
        ret = False
        break
    return ret

  def plane_plane_plane_tet_out(self,
                                polytope: Polytope, 
                                f1: AbstractHalfspace, 
                                f2: AbstractHalfspace, 
                                f3: AbstractHalfspace, 
                                polytopeMap: PolytopeMap, 
                                currentpIndex1: int,
                                currentpIndex2: int, 
                                currentpIndex3: int) -> OrientResult:
    if not self.implicit_point_in_polytope_TPI(polytope, f1, f2, f3):
      return IN

    ret = OUT
    for i, p in enumerate(polytopeMap):
      if i not in {currentpIndex1, currentpIndex2, currentpIndex3} and self.implicit_point_in_polytope_TPI(f1, f2, f3, p):
        ret = IN
        break

    return ret

  def check_c4(self,
               polytope: Polytope,
               polytopeSet: PolytopeMap) -> OrientResult:
    faces = [(face, i) for i, p in enumerate(polytopeSet) for face in p]
    for (fi, i), (fj, j), (fk, k) in itertools.combinations(faces, 3): # no repetimos ternas
      if self.plane_plane_plane_tet_out(polytope, fi, fj, fk, polytopeSet, i, j, k) == OUT:
        return OUT
    return IN

  # chequea C1, C2 Y C3 para las caras del politopo
  def envelope_check_faces(self, 
                           polytope: Polytope, 
                           polytopeSet: PolytopeMap, 
                           verticesIndex: VerticesIndex, 
                           edgesIndex: EdgesIndex) -> bool:
    faces = polytope.get_faces()
    ret = True
    for f in faces:
      coverage = self._checker.envelope_check(f, polytopeSet, verticesIndex, edgesIndex)
      if coverage == OUT:
        ret = False
        break
    return ret

  # chequea un politopo 3d
  def envelope_check(self, 
                     polytope: Polytope, 
                     polytopeSet: PolytopeMap, 
                     verticesIndex: VerticesIndex, 
                     edgesIndex: EdgesIndex) -> OrientResult: 
    ret = IN
    if not self.envelope_check_triangles(polytope, polytopeSet, verticesIndex, edgesIndex):
      ret = OUT
    elif self.check_c4(polytope, polytopeSet) == OUT:
      log.info("Falla C4")
      ret = OUT
    else:
      log.info("Todo OK")
    return ret