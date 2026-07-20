from .predicates import AbstractPredicates
from .predicates_2d import Predicates2d

PredicatesFactory = {2: Predicates2d} # agregar los predicados para cada dimensión

__all__ = ["AbstractPredicates", "PredicatesFactory"] 