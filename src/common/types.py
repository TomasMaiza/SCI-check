from geometry.abstract_structs import AbstractPoint, Halfspace

type PolytopeMap = list[list[Halfspace]]
# diccionario que relaciona cada subregion con un conjunto de los semiespacios que la definen

type SerializedPolytopeMap = list[list[list[float]]] # lista de subespacios para matlab

type Point = tuple[float, ...] # un punto es una tupla de flotantes

type Edge = tuple[Point, Point] # una arista es una tupla de puntos

type VerticesIndex = dict[AbstractPoint, bool]
# tabla que indexa los vértices para no repetir chequeos en la condición C1. El valor indica si
# ya fue verificado.

type EdgesIndex = dict[Edge, bool]
# ídem para aristas en la condición C2