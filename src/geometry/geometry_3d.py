import numpy as np
from .geometry import AbstractGeometry
from .structs_3d import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from .polytope import Polytope
  from src.common.types import Edge

class Geometry3d(AbstractGeometry):
  # geometría 3d
  def create_point(self, coord: tuple[float, ...]) -> Point3D: # crea un punto
    return Point3D(x = coord[0], y = coord[1], z = coord[2])

  def create_simplex(self, vertices: tuple[Point3D, ...]) -> Tetrahedron3D:
    return Tetrahedron3D(vertices)

  def create_halfspace(self, points: tuple[Point3D, Point3D]) -> Halfspace3D: 
    # crea un semiespacio
    return Halfspace3D(points = points)

  def create_halfspace_from_vector(self, normalVector: np.ndarray, b: float) -> Halfspace3D: # crea un semiespacio
    return Halfspace3D(normalVector = normalVector, b = b)

  def get_dimension(self) -> int: # retorna la dimensión
    return 3

  def create_halfspaces_list(self, subregionPolytope: 'Polytope') -> list[Halfspace3D]:
    # REVISAR
    matrixA, vectorB = subregionPolytope.get_hrep()
    dimension = 3
    halfspacesList = []
      
    for i in range(len(vectorB)):
      normalVector = matrixA[i]
      offset = vectorB[i]

      maxIndex = np.argmax(np.abs(normalVector))
      if abs(normalVector[maxIndex]) < 1e-12:
        continue
              
      basePointCoords = np.zeros(dimension)
      basePointCoords[maxIndex] = offset / normalVector[maxIndex]
      pointsCoordsList = [basePointCoords]
          
      for j in range(dimension):
        if j != maxIndex:
          currentPointCoords = np.copy(basePointCoords)
          currentPointCoords[j] += 1.0
          currentPointCoords[maxIndex] -= normalVector[j] / normalVector[maxIndex]
          pointsCoordsList.append(currentPointCoords)
                  
      # 3. Escudo protector de orientación para 3D (Regla de la mano derecha)
      vector1 = pointsCoordsList[1] - pointsCoordsList[0]
      vector2 = pointsCoordsList[2] - pointsCoordsList[0]
      computedCross = np.cross(vector1, vector2)
          
      if np.dot(computedCross, normalVector) < 0:
        # Invertimos dos puntos para corregir el sentido de la normal
        pointsCoordsList[1], pointsCoordsList[2] = pointsCoordsList[2], pointsCoordsList[1]
              
          # 4. Creamos los puntos abstractos mediante la fábrica y armamos el semiespacio
      abstractPoints = tuple(self.create_point(tuple(coords)) for coords in pointsCoordsList)
      halfspace = self.create_halfspace(abstractPoints)
      halfspacesList.append(halfspace)
          
    return halfspacesList

  def get_polytope_edges(self, polytope: 'Polytope') -> list['Edge']:
    # devuelve una lista de las aristas de un politopo como una lista de (Point2D, Point2D)
    edges = polytope.get_edges()
    geomEdges = []
    for e in edges:
      v1, v2 = Point3D(x = e[0][0], y = e[0][1], z = e[0][2]), Point3D(x = e[1][0], y = e[1][1], z = e[1][2])
      geomEdges.append((v1, v2))
    return geomEdges