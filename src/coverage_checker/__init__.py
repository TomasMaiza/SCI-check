from .coverage_checker import CoverageChecker
from .coverage_checker_3d import CoverageChecker3D
from .strategy import CoverageCheckStrategy
from .predicates import *

CoverageCheckerFactory = {2: CoverageChecker, 3: CoverageChecker3D}

__all__ = ["CoverageChecker", 
           "CoverageCheckStrategy", 
           "AbstractPredicates", 
           "PredicatesFactory",
           "CoverageCheckerFactory"]