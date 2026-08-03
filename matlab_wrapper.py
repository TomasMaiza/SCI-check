import sys
import os

currentDir = os.path.dirname(os.path.abspath(__file__))
srcPath = os.path.join(currentDir, 'src')

if srcPath not in sys.path:
    sys.path.insert(0, srcPath)

import numpy as np
from sci import SCIChecker
from geometry import *
from coverage_checker import *
import polytope as pc
from affine_system import *

class MatlabWrapperSCI:
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

  def create_sas(self, systemRaw: list[tuple[list[list[float]], list[float]]]):
    # inicializa el sistema afín conmutado
    modesDict = {}
    for mode, (ARaw, bRaw) in enumerate(systemRaw):
      A = np.array(ARaw, dtype=np.float64)
      b = np.array(bRaw, dtype=np.float64)
      modesDict[mode] = (A, b)
    self._sas = SwitchedAffineSystem(modesDict)

  def checking_sci(self, 
                   polytopeVerticesRaw: list[list[float]], 
                   systemRaw: list[tuple[list[list[float]], list[float]]],  # lista de tuplas (A, b)
                   dwellTime: float, 
                   K: int, 
                   dimension: int) -> bool:
    # recibe listas crudas desde MATLAB, arma la geometría y corre el SCIChecker.
    self.create_geometry_and_predicates(dimension)
    self.create_polytope(polytopeVerticesRaw)
    self.create_sas(systemRaw)
    checker = SCIChecker(self._geom, self._preds, self._polytope, self._subregions, self._sas)
    isSCI, subregions = checker.sci_check(dwellTime, K)
    return isSCI