import polytope as pc
from geometry.abstract_structs.halfspace import AbstractHalfspace

type PolytopeMap = list[set[AbstractHalfspace]]
# diccionario que relaciona cada subregion con un conjunto de los semiespacios que la definen