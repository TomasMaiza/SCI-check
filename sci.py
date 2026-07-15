from geometry.geometry import AbstractGeometry
from coverage_checker.predicates import AbstractPredicates
from geometry.abstract_structs.simplex import AbstractSimplex
from common.enums import OrientResult
from common.types import PolytopeMap, VerticesIndex
from coverage_checker.coverage_checker import CoverageChecker
from triangulation import PolytopeTriangulator, DelaunayTriangulation
import polytope as pc
import numpy as np
from scipy.spatial import ConvexHull
from aabbtree import AABB, AABBTree

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

  def get_aabb_limits_p(self) -> list[list[tuple[float, float]]]:
    limits = []
    for p in self._subregions:
      p1, p2 = p[0].get_points()
      xmin = min(p1.x, p2.x)
      xmax = max(p1.x, p2.x)
      ymin = min(p1.y, p2.y)
      ymax = max(p1.y, p2.y)
      for f in p[1:]:
        p1, p2 = f.get_points()
        xmin = min(xmin, p1.x, p2.x)
        xmax = max(xmax, p1.x, p2.x)
        ymin = min(ymin, p1.y, p2.y)
        ymax = max(ymax, p1.y, p2.y)
      limits.append([(xmin, xmax), (ymin, ymax)])
    return limits
  
  def _get_aabb_limits_t(self, triangle: AbstractSimplex) -> list[tuple[float, float]]:
    v1, v2, v3 = triangle.get_vertices()
    xmin = min(v1.x, v2.x, v3.x)
    xmax = max(v1.x, v2.x, v3.x)
    ymin = min(v1.y, v2.y, v3.y)
    ymax = max(v1.y, v2.y, v3.y)
    return [(xmin, xmax), (ymin, ymax)]

  def create_aabb_tree(self):
    self._aabbTree = AABBTree() # creo el árbol aabb
    plimits = self.get_aabb_limits_p() # obtengo los límites

    for i, lim in enumerate(plimits): # lleno el árbol
        caja = AABB(lim)
        self._aabbTree.add(caja, i)

  def _get_filtered_map(self, triangle: AbstractSimplex):
    limits = self._get_aabb_limits_t(triangle)
    box = AABB(limits)
    indices = self._aabbTree.overlap_values(box)
    filteredMap = [self._subregions[i] for i in indices]
    return filteredMap

  def check_coverage(self) -> bool: # itera sobre los triángulos
    coverageChecker = CoverageChecker(self._geometry, self._predicates)
    ret = True
    for t in self._triangles:
      filteredMap = self._get_filtered_map(t)
      check = coverageChecker.envelope_check(t, filteredMap, self._verticesIndex, self._edgesIndex)
      if check == OUT:
        ret = False
        break
    return ret

  def sci_check(self) -> bool: # hace todo el proceso
    self.triangulate_polytope()
    # get_subregions
    self.create_aabb_tree() # estrategia de aceleración 1
    return self.check_coverage()