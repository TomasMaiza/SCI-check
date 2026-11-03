from coverage_checker import CoverageCheckStrategy, CoverageChecker, PredicatesFactory, CoverageCheckerFactory
from geometry import Polytope
from common import ON, OUT, IN
from affine_system import SwitchedAffineSystem
from polytope_subregions import FloatSubregions, IntervalSubregions

"""
Clase principal para ejecutar el algoritmo. Permite inicializarla con el politopo y el sistema afín conmutado,
 genera las subregiones y verifica la cobertura. 
"""

class SCIChecker():
  def __init__(self, 
               dimension: int,
               polytope: Polytope, 
               sas: SwitchedAffineSystem):
    """
    La clase se inicializa con el politopo, el sistema afín conmutado y la dimensión
    """
    self._predicates = PredicatesFactory[dimension]()
    self._polytope = polytope
    self._sas = sas
    self._subregionsAlgorithm = IntervalSubregions(dimension) # le paso acá el método de aprox?
    covChecker = CoverageCheckerFactory[dimension]
    self._coverageChecker = covChecker(self._predicates)

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