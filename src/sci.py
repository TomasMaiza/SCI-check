from coverage_checker import CoverageCheckStrategy, CoverageChecker, AbstractPredicates
from geometry import Polytope
from common import ON, OUT, IN
from triangulation import *
import numpy as np
from aabbtree import AABB, AABBTree
from affine_system import SwitchedAffineSystem
from polytope_subregions import SubregionsStrategy, Subregions

class SCIChecker():
  def __init__(self, 
               dimension: int,
               predicates: AbstractPredicates, 
               coverageChecker: CoverageCheckStrategy,
               polytope: Polytope, 
               sas: SwitchedAffineSystem):
    self._predicates = predicates
    self._polytope = polytope
    self._sas = sas
    self._subregionsAlgorithm = Subregions(dimension)
    self._coverageChecker = coverageChecker(predicates)

  def get_subregions(self, dwellTime: float, K: int):
    self._subregions = self._subregionsAlgorithm.get_subregions(self._sas, self._polytope, dwellTime, K)

  def check_coverage(self) -> bool:
    ret = True
    check = self._coverageChecker.envelope_check(self._polytope, self._subregions)
    if check == OUT:
      ret = False
    return ret

  def sci_check(self, dwellTime: float, K: int) -> tuple[bool, list[Polytope]]: # hace todo el proceso
    self.get_subregions(dwellTime, K)
    cov = self.check_coverage()
    subregions = self._subregions
    self._subregions = [] # reinicializamos para un próximo chequeo con otros parámetros
    return cov, subregions