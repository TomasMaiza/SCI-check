from geometry.geometry import AbstractGeometry
from coverage_checker.predicates import AbstractPredicates
from common.enums import OrientResult
from common.types import PolytopeMap
from coverage_checker.coverage_checker import CoverageChecker
from triangulation import PolytopeTriangulator, DelaunayTriangulation
import polytope as pc
import numpy as np

IN = OrientResult.IN
OUT = OrientResult.OUT

# acá va la interfaz de la librería con la lógica de presentación

'''
En principio recibe un politopo y sus subregiones.
Triangula el politopo y debe asignarle índices a los vértices (visitor? hacerlo después?)
Por ahora no se fija en los índices y hace trabajo de más
Hay que setear geometría y predicados acá?
'''

class SCIChecker():
  def __init__(self, geometry: AbstractGeometry, 
               predicates: AbstractPredicates, polytope: pc.Polytope, subregions: PolytopeMap):
    self._geometry = geometry
    self._predicates = predicates
    self._polytope = polytope
    self._subregions = subregions # esto después vuela

  def triangulate_polytope(self): # asignar índices a vértices y guardar todo en variables?
    triangulator = PolytopeTriangulator(DelaunayTriangulation)
    self._triangles = triangulator.triangulate(self._polytope)
    # acá indexar vértices

  def get_subregions(self): # para más adelante
    pass

  def check_coverage(self) -> bool: # itera sobre los triángulos
    coverageChecker = CoverageChecker(self._geometry, self._predicates)
    ret = True
    for t in self._triangles:
      check = coverageChecker.envelope_check(t, self._subregions)
      if check == OUT:
        ret = False
        break
    return ret


  def sci_check(self) -> bool: # hace todo el proceso
    self.triangulate_polytope();
    # get_subregions
    return self.check_coverage();

  # capaz podría haber alguna función más para graficar