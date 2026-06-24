from geometry.geometry import AbstractGeometry
from coverage_checker.predicates import AbstractPredicates
from common.enums import OrientResult
from coverage_checker.coverage_checker import CoverageChecker
from triangulation import PolytopeTriangulator, DelaunayTriangulation
import polytope as pc
import numpy as np

# acá va la interfaz de la librería con la lógica de presentación

'''
En principio recibe un politopo y sus subregiones.
Triangula el politopo y debe asignarle índices a los vértices (visitor? hacerlo después?)
Por ahora no se fija en los índices y hace trabajo de más
Hay que setear geometría y predicados acá?
'''

class SCIChecker():
  def __init__(self, geometry: AbstractGeometry, 
               predicates: AbstractPredicates, polytope: pc.Polytope, subregions: ):
    self._polytope = polytope

  def triangulate_polytope(self): # asignar índices a vértices y guardar todo en variables?
    triangulator = PolytopeTriangulator(DelaunayTriangulation)
    self._triangles = triangulator.triangulate(self._polytope)

  def get_subregions(self): # para más adelante
    pass

  def check_coverage(self) -> bool: # itera sobre los triángulos
    pass

  def sci_check(self) -> bool: # hace todo el proceso
    pass

  # capaz podría haber alguna función más para graficar