from abc import ABC, abstractmethod
import numpy as np
from typing import Optional
from geometry import AbstractPoint, Halfspace, Hyperplane
from .polytope import Polytope
import polytope as pc
from .polytope_conc_2d import ConcretePolytope2D

class ConcretePolytope(Polytope):
  # Implementación de politopos

  _intDim: int # dimensión intrínseca del politopo
  _ambDim: int # dimensión ambiental
  _boundaries: list['Polytope']
  _vertices: np.ndarray
  _A: np.ndarray 
  _b: np.ndarray
  _supporting_hyperplane: Hyperplane
  _halfspaces: list[Halfspace]

  def __init__(self, 
               intDim: int,
               ambDim: int,
               vertices: Optional['tuple[AbstractPoint, ...]'] = None, 
               A: Optional['np.ndarray'] = None, 
               b: Optional['np.ndarray'] = None):
    self._intDim = intDim
    self._ambDim = ambDim
    if A is not None and b is not None and vertices is None:
      self._A = A
      self._b = b
      self._set_vertices_from_hrep()
    elif A is None and b is None and vertices is not None and len(vertices) > 2:
      pointsArray = np.array([list(v.get_point()) for v in vertices])
      self._vertices = pointsArray  
      self._set_h_rep_from_vertices()
    else:
      raise ValueError("Inicialización inválida: Proveer vértices o (A, b)")

  def _set_vertices_from_hrep(self):
    # calcula los vértices si se inicializó con h-rep
    poly = pc.Polytope(self._A, self._b)
    self._vertices = pc.extreme(poly)

  def _set_h_rep_from_vertices(self):
    # calcula A y b si se inicializó con vértices
    poly = pc.qhull(self._vertices)
    poly = pc.reduce(poly)
    self._A, self._b = poly.A, poly.b

  def get_vertices(self) -> np.ndarray:
    if self._vertices is not None:
      return self._vertices

  def get_hrep(self) -> tuple[np.ndarray, np.ndarray]:
    # permite obtener las matrices A y b que definen al politopo (Ax <= b)
    if self._A is not None and self._b is not None:
      return self._A, self._b

  def get_edges(self) -> list[tuple[tuple[float, ...], tuple[float, ...]]]:
    # retorna las aristas del politopo
    pass

  def get_boundaries(self):
    if hasattr(self, '_boundaries') and self._boundaries:
      return self._boundaries

    self._boundaries = []
      
    # Si llegamos a la dimensión mínima útil (ej: vértice), cortamos la recursión
    # if self._intDim <= 0:
    #  return self._boundaries

    # Tolerancia estándar para compensar el punto flotante de la librería polytope
    TOL = 1e-8 

    # Iteramos sobre cada inecuación (fila de A y b)
    for i in range(len(self._A)):
      normal = self._A[i]
      offset = self._b[i]

      # MAGIA NUMPY: Calculamos la distancia de TODOS los vértices al plano de una sola vez
      # Ecuación: Ax - b. Si da ~0, el vértice está en el plano.
      distances = np.dot(self._vertices, normal) - offset # OJO CON ERROR DE CÁLCULO

      # Obtenemos los índices de los vértices que cumplen la condición
      in_plane_indices = np.where(np.isclose(distances, 0.0, atol=TOL))[0]

      # Un hiperplano de dimensión N necesita al menos N vértices para formar una cara
      # Ej: Una cara 2D necesita mínimo 3 vértices. Si tiene menos, no es una cara válida.
      if len(in_plane_indices) >= self._intDim:
        face_vertices = self._vertices[in_plane_indices]

        # diccionario del composite para instanciar según dimensión (si es hoja o no)
        if self._intDim == 3:
          boundary = ConcretePolytope2D(
            intDim = 2,
            ambDim = self._ambDim,
            vertices = face_vertices
          )

        # Instanciamos la cara reduciendo la dimensión intrínseca
        else:
          boundary = ConcretePolytope(
            intDim=self._intDim - 1,
            ambDim=self._ambDim,
            vertices=face_vertices
          )
          
      # (Opcional a futuro): face._supp_hyperplane = Hyperplane(normal, offset)
          
      self._boundaries.append(boundary)

    return self._boundaries

  def get_halfspaces(self) -> list[Halfspace]:
    # devuelve la lista de los semiespacios que definen al politopo
    if self._halfspaces is None:
      A, b = self._A, self._b
      self._halfspaces = []
      for i in range(len(b)):
        A_face = A[i]
        b_face = b[i]
        hs = Halfspace(normalVector=A_face, b=b_face)
        self._halfspaces.append(hs)
    return self._halfspaces

  def get_supporting_hyperplane(self) -> Hyperplane:
    # retorna el hiperplano que contiene al politopo si intDim < ambDim
    if self._intDim == self._ambDim:
      return
    points = []
    for i in range(self._intDim):
      points[i] = self._vertices[i]
    return Hyperplane(points)

  def reduce(self):
    # elimina las inecuaciones redundantes
    pass