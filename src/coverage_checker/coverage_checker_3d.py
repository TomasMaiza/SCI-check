from .predicates import AbstractPredicates, Predicates3d
from geometry import *
from common import *
from .strategy import CoverageCheckStrategy
from .coverage_checker import CoverageChecker
import logging
import itertools

# Patrón Decorator
class CoverageChecker3D(CoverageChecker):
  def __init__(self, 
               predicates: AbstractPredicates) -> None:
    self._checker = CoverageChecker(Predicates3d())
    self._predicates = Predicates3d()

  def implicit_point_in_polytope_TPI(self, # la muevo a predicates3d?
                                     f1: Halfspace,
                                     f2: Halfspace, 
                                     f3: Halfspace, 
                                     p: Polytope) -> bool:
    ret = True
    halfspaces = p.get_halfspaces()
    if len(halfspaces) == 0:
      ret = False
    for fp in halfspaces:
      ori = self._predicates.orient_TPI_halfspaces(f1, f2, f3, fp)
      if ori == OUT:
        ret = False
        break
    return ret

  def plane_plane_plane_poly_out(self,
                                polytope: Polytope, 
                                f1: Halfspace, 
                                f2: Halfspace, 
                                f3: Halfspace, 
                                subregionsMap: list[Polytope], 
                                currentpIndex1: int,
                                currentpIndex2: int, 
                                currentpIndex3: int) -> OrientResult:
    # punto implícito: intersección de 3 planos
    if not self._predicates.implicit_point_in_polytope_3d(polytope, f1, f2, f3):
      return IN
    # faces = polytope.get_boundaries()
    ret = OUT
    for i, p in enumerate(subregionsMap):
      #if i not in {currentpIndex1, currentpIndex2, currentpIndex3} and self.implicit_point_in_polytope_TPI(f1, f2, f3, p):
      if i not in {currentpIndex1, currentpIndex2, currentpIndex3} and self.implicit_point_in_polytope_TPI(f1, f2, f3, p):
        ret = IN
        break

    return ret

  def check_c4(self,
               polytope: Polytope,
               subregionsMap: list[Polytope]) -> OrientResult:
    faces = [(face, i) for i, p in enumerate(subregionsMap) for face in p]
    for (fi, i), (fj, j), (fk, k) in itertools.combinations(faces, 3): # no repetimos ternas
      if self.plane_plane_plane_poly_out(polytope, fi, fj, fk, subregionsMap, i, j, k) == OUT:
        return OUT
    return IN

  # chequea C1, C2 Y C3 para las caras del politopo
  def envelope_check_faces(self, 
                           polytope: Polytope, 
                           subregionsMap: list[Polytope]) -> bool:
    faces = polytope.get_boundaries()
    ret = True
    for f in faces:
      coverage = self._checker.envelope_check(f, subregionsMap)
      if coverage == OUT:
        ret = False
        break
    return ret

  # chequea un politopo 3d
  def envelope_check(self, 
                     polytope: Polytope, 
                     subregionsMap: list[Polytope]) -> OrientResult: 
    ret = IN
    if not self.envelope_check_faces(polytope, subregionsMap):
      ret = OUT
    elif self.check_c4(polytope, subregionsMap) == OUT:
      log.info("Falla C4")
      ret = OUT
    else:
      log.info("Todo OK")
    return ret