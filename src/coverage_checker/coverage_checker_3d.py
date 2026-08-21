from .predicates import AbstractPredicates
from geometry import *
from geometry.structs_3d import *
from common import *
from .strategy import CoverageCheckStrategy
from .coverage_checker import CoverageChecker
import logging
import itertools

class CoverageChecker3D(CoverageChecker):
  def __init__(self, 
               geometry: AbstractGeometry, 
               predicates: AbstractPredicates) -> None:
    self._checker = CoverageChecker(geometry, predicates)

  def check_c4(self,
               tetrahedron: Tetrahedron3D,
               polytopeSet: PolytopeMap) -> OrientResult:
    faces = [(face, i) for i, p in enumerate(polytopeSet) for face in p]
    for (fi, i), (fj, j), (fk, k) in itertools.combinations(faces, 3): # no repetimos ternas
      if self.plane_plane_plane_tet_out(tetrahedron, fi, fj, fk, polytopeSet, i, j, k) == OUT:
        return OUT
    return IN

  # chequea triángulos
  def envelope_check_triangles(self, 
                              tetrahedron: Tetrahedron3D, 
                              polytopeSet: PolytopeMap, 
                              verticesIndex: VerticesIndex, 
                              edgesIndex: EdgesIndex) -> bool:
    triangles = tetrahedron.get_faces()
    ret = True
    for t in triangles:
      coverage = self._checker.envelope_check(t, polytopeSet, verticesIndex, edgesIndex)
      if not coverage:
        break
    return ret

  # chequea UN tetredro
  def envelope_check(self, 
                     tetrahedron: Tetrahedron3D, 
                     polytopeSet: PolytopeMap, 
                     verticesIndex: VerticesIndex, 
                     edgesIndex: EdgesIndex) -> OrientResult: 
    ret = IN
    if not self.envelope_check_triangles(tetrahedron, polytopeSet, verticesIndex, edgesIndex):
      ret = OUT
    if self._checker.check_c4(tetrahedron, polytopeSet, edgesIndex) == OUT:
      log.info("Falla C4")
      ret = OUT
    else:
      log.info("Todo OK")
    return ret