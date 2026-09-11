from .predicates import AbstractPredicates, Predicates3d
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
    self._checker = CoverageChecker(geometry, Predicates3d())
    self._geometry = geometry
    self._predicates = Predicates3d()

  '''
  def implicit_point_in_tet_TPI(self, # revisar estas cosas. Probabemente la del tetraedro se va?
                                        polytope: Polytope, 
                                        f1: AbstractHalfspace, 
                                        f2: AbstractHalfspace, 
                                        f3: AbstractHalfspace):
    ret = True
    faces = polytope.get_faces()
    for p in faces:
      vertices = p.get_vertices()
      a = Point3D(x=float(vertices[0][0]), y=float(vertices[0][1]), z=float(vertices[0][2]))
      b = Point3D(x=float(vertices[1][0]), y=float(vertices[1][1]), z=float(vertices[1][2]))
      c = Point3D(x=float(vertices[2][0]), y=float(vertices[2][1]), z=float(vertices[2][2]))
      f = Halfspace3D(points = (a, b, c)) # VER ORIENT TPI PARA POLITOPOS
      ori = self._predicates.orient_TPI(f1, f2, f3, f)
      if ori == OUT:
        ret = False
        break
    return ret
  '''

  def implicit_point_in_polytope_TPI(self, # la muevo a predicates3d?
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

  def plane_plane_plane_poly_out(self,
                                polytope: Polytope, 
                                f1: AbstractHalfspace, 
                                f2: AbstractHalfspace, 
                                f3: AbstractHalfspace, 
                                polytopeMap: PolytopeMap, 
                                currentpIndex1: int,
                                currentpIndex2: int, 
                                currentpIndex3: int) -> OrientResult:
    # punto implícito: intersección de 3 planos
    if not self._predicates.implicit_point_in_polytope_3d(polytope, f1, f2, f3):
      return IN
    faces = polytope.get_faces()
    ret = OUT
    for i, p in enumerate(faces):
      #if i not in {currentpIndex1, currentpIndex2, currentpIndex3} and self.implicit_point_in_polytope_TPI(f1, f2, f3, p):
      if i not in {currentpIndex1, currentpIndex2, currentpIndex3} and self.implicit_point_in_polytope_3d(f1, f2, f3, p):
        ret = IN
        break

    return ret

  def check_c4(self,
               polytope: Polytope,
               polytopeSet: PolytopeMap) -> OrientResult:
    faces = [(face, i) for i, p in enumerate(polytopeSet) for face in p]
    for (fi, i), (fj, j), (fk, k) in itertools.combinations(faces, 3): # no repetimos ternas
      if self.plane_plane_plane_poly_out(polytope, fi, fj, fk, polytopeSet, i, j, k) == OUT:
        return OUT
    return IN

  # chequea C1, C2 Y C3 para las caras del politopo
  def envelope_check_faces(self, 
                           polytope: Polytope, 
                           polytopeSet: PolytopeMap) -> bool:
    faces = polytope.get_faces()
    ret = True
    for f in faces:
      coverage = self._checker.envelope_check(f, polytopeSet)
      if coverage == OUT:
        ret = False
        break
    return ret

  # chequea un politopo 3d
  def envelope_check(self, 
                     polytope: Polytope, 
                     polytopeSet: PolytopeMap) -> OrientResult: 
    ret = IN
    if not self.envelope_check_faces(polytope, polytopeSet):
      ret = OUT
    elif self.check_c4(polytope, polytopeSet) == OUT:
      log.info("Falla C4")
      ret = OUT
    else:
      log.info("Todo OK")
    return ret