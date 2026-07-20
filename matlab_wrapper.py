import sys
import os

currentDir = os.path.dirname(os.path.abspath(__file__))
srcPath = os.path.join(currentDir, 'src')

# 2. Le inyectamos esta ruta al cerebro del intérprete de Python de MATLAB
if srcPath not in sys.path:
    sys.path.insert(0, srcPath)

import numpy as np
from sci import SCIChecker
from geometry import *
from coverage_checker import *
import polytope as pc
from scipy.spatial import ConvexHull

class MatlabWrapper:
  def create_geometry_and_predicates(self, dimension: int):
    # inicializa la geometría y los predicados
    geomClass = GeometryFactory[dimension]
    predClass = PredicatesFactory[dimension]
    self._geom = geomClass()
    self._preds = predClass()
  
  def create_polytope(self, polytopeVerticesRaw: list[list[float]]):
    # se inicializa el politopo
    polytopeVertices = np.array(polytopeVerticesRaw, dtype=float) # vértices del politopo
    self._polytope = pc.qhull(polytopeVertices) # se crea el politopo

  def create_subregions(self, subregionsVerticesRaw: list[list[list[float]]]):
    # crea la lista de semiespacios que definen cada subregión politópica
    self._subregions = []
    for sub in subregionsVerticesRaw:
      numVertices = len(sub) # sub es una lista de coordenadas [[x1, y1], [x2, y2], ...]
      if numVertices < 3: # un polígono necesita al menos 3 vértices
        continue 
        
      subArray = np.array(sub, dtype=float) # convertimos la subregión a un array de numpy
      hull = ConvexHull(subArray) # ordenamos los vértices en sentido antihorario con ConvexHull
      sortedVertices = subArray[hull.vertices] # LO DE ORDENAR SE PODRÍA HACER CON UN STRATEGY
        
      numVertices = len(sortedVertices)
      subHalfspaces = []
      for i in range(numVertices): # iteramos para armar los bordes del politopo (v1, v2)
        v1 = sortedVertices[i]
        v2 = sortedVertices[(i + 1) % numVertices]
        p1 = self._geom.create_point(v1)
        p2 = self._geom.create_point(v2)
        hs = self._geom.create_halfspace((p1, p2))
        subHalfspaces.append(hs)
            
      self._subregions.append(subHalfspaces) # agregamos la lista de semiespacios de la subregión

  def checking_sci(self, polytopeVerticesRaw: list[list[float]], subregionsVerticesRaw: list[list[list[float]]], dimension: int) -> bool:
    # recibe listas crudas desde MATLAB, arma la geometría y corre el SCIChecker.
    self.create_geometry_and_predicates(dimension)
    self.create_polytope(polytopeVerticesRaw)
    self.create_subregions(subregionsVerticesRaw)
    checker = SCIChecker(self._geom, self._preds, self._polytope, self._subregions)
    return checker.sci_check()