from geometry.geometry import AbstractGeometry
from coverage_checker.predicates import AbstractPredicates
from common.enums import OrientResult
from common.types import PolytopeMap, VerticesIndex
from coverage_checker.coverage_checker import CoverageChecker
from triangulation import PolytopeTriangulator, DelaunayTriangulation
import polytope as pc
import numpy as np
from scipy.spatial import ConvexHull

IN = OrientResult.IN
OUT = OrientResult.OUT
ON = OrientResult.ON

'''
En principio recibe un politopo y sus subregiones.
Triangula el politopo y debe asignarle índices a los vértices (visitor? hacerlo después?)
Por ahora no se fija en los índices y hace trabajo de más
'''

class SCIChecker():
  def __init__(self, geometry: AbstractGeometry, 
               predicates: AbstractPredicates, polytope: pc.Polytope, subregions: PolytopeMap):
    self._geometry = geometry
    self._predicates = predicates
    self._polytope = polytope
    self._subregions = subregions # esto después vuela
    # en qué orden están las subregiones?

  def triangulate_polytope(self): # asignar índices a vértices y guardar todo en variables?
    triangulator = PolytopeTriangulator(DelaunayTriangulation())
    triangles = triangulator.triangulate(self._polytope)
    self._triangles = [] # lista de triángulos en los que se dividió el politopo
    # convertimos a Simplex
    for t in triangles:
      # t tiene la forma [[x1, y1], [x2, y2], [x3, y3]]
      v1 = self._geometry.create_point((t[0][0], t[0][1]))
      v2 = self._geometry.create_point((t[1][0], t[1][1]))
      v3 = self._geometry.create_point((t[2][0], t[2][1]))
      simplex = self._geometry.create_simplex((v1, v2, v3))
      self._triangles.append(simplex)
    self._set_indices()

  def _set_indices(self):
    self._verticesIndex = {} # diccionario para ver si cada vértice ya se chequeó o no
    self._edgesIndex = {} # diccionario para ver si cada arista ya se chequeó o no
    for t in self._triangles:
      vertices = t.get_vertices()
      # si dos vértices tienen la misma coordenada ya estarían marcados en el diccionario
      # como visitados con visitar uno solo
      for v in vertices:
        self._verticesIndex[v] = False # ningún vértice fue chequeado aún

      edges = t.get_edges()
      for e in edges:
        self._edgesIndex[e] = False
      

  def get_subregions(self): # para más adelante
    pass
    # cuando haga esto tengo que ordenar los semiespacios que definen cada subregión
    # podría hacerse con scipy.spatial.ConvexHull
    # eso me ordena los vértices, luego creo los semiespacios

  def check_coverage(self) -> bool: # itera sobre los triángulos
    coverageChecker = CoverageChecker(self._geometry, self._predicates)
    ret = True
    for t in self._triangles:
      check = coverageChecker.envelope_check(t, self._subregions, self._verticesIndex, self._edgesIndex)
      if check == OUT:
        ret = False
        break
    return ret

  def sci_check(self) -> bool: # hace todo el proceso
    self.triangulate_polytope();
    # get_subregions
    return self.check_coverage();

  # capaz podría haber alguna función más para graficar