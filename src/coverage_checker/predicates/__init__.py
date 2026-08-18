from .predicates import AbstractPredicates
from .predicates_2d import Predicates2d
from .predicates_3d import Predicates3d

PredicatesFactory = {2: Predicates2d, 3: Predicates3d} # agregar los predicados para cada dimensión

__all__ = ["AbstractPredicates", "PredicatesFactory"] 