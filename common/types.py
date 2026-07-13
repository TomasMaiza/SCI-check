from geometry.abstract_structs.halfspace import AbstractHalfspace
from geometry.abstract_structs.point import AbstractPoint

type PolytopeMap = list[list[AbstractHalfspace]]
# diccionario que relaciona cada subregion con un conjunto de los semiespacios que la definen

type Edge = tuple[AbstractPoint, AbstractPoint] # una arista es una tupla de puntos

type VerticesIndex = dict[AbstractPoint, bool]
# tabla que indexa los vértices para no repetir chequeos en la condición C1. El valor indica si
# ya fue verificado.

type EdgesIndex = dict[Edge, bool]
# ídem para aristas en la condición C2