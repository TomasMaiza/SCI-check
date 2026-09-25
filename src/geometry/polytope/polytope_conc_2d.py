from abc import ABC, abstractmethod
import numpy as np
from typing import Optional, TYPE_CHECKING
from geometry import AbstractPoint, Halfspace, Hyperplane
from .polytope import Polytope
import polytope as pc
from scipy.spatial import ConvexHull
import itertools

if TYPE_CHECKING:
  from src.common.types import Point, Edge

class ConcretePolytope2D(Polytope):
  # Implementación de politopos 2D (hoja del Composite)

  _ambDim: int # dimensión ambiental
  _boundaries: list['Polytope']
  _vertices: np.ndarray
  _A: np.ndarray 
  _b: np.ndarray
  _supporting_hyperplane: Hyperplane
  _halfspaces: list[Halfspace]
  _centroid: 'Point'

  def __init__(self, 
               intDim: int,
               ambDim: int,
               vertices: Optional['list[Point]'] = None,
               verticesnp: Optional['np.ndarray'] = None,
               A: Optional['np.ndarray'] = None, 
               b: Optional['np.ndarray'] = None):

    if (A is None or b is None) and vertices is None and verticesnp is None:
      raise ValueError("Inicialización inválida: Proveer vértices o (A, b)")

    self._intDim = 2
    self._ambDim = ambDim
    self._halfspaces = None
    self._centroid = None
    self._A = A
    self._b = b

    if verticesnp is not None:
      self._vertices = verticesnp
    elif vertices is not None:
      self._vertices = np.array(vertices) 
    else:
      self._vertices = None

    if self._vertices is None:
      self._set_vertices_from_hrep()
    elif self._A is None or self._b is None:
      self._set_h_rep_from_vertices()
    self.reduce()

  def _set_vertices_from_hrep(self):
    # calcula los vértices si se inicializó con h-rep
    poly = pc.Polytope(self._A, self._b)
    self._vertices = pc.extreme(poly)

  def _set_h_rep_from_vertices(self):
    # calcula A y b si se inicializó con vértices
    poly = pc.qhull(self._vertices)
    self._A, self._b = poly.A, poly.b

  def get_vertices(self) -> np.ndarray:
    if self._vertices is not None:
      return self._vertices

  def get_hrep(self) -> tuple[np.ndarray, np.ndarray]:
    # permite obtener las matrices A y b que definen al politopo (Ax <= b)
    if self._A is not None and self._b is not None:
      return self._A, self._b

  def get_edges(self) -> list['Edge']:
    # retorna las aristas del politopo
    if self._vertices is None:
      return [] 
        
    hull = ConvexHull(self._vertices)
    unique_edges = set()
    
    for simplex in hull.simplices:
      # itertools.combinations saca todos los pares posibles del simplex
      # En 2D saca 1 par. En 3D saca 3 pares (los 3 lados del triángulo).
      for i, j in itertools.combinations(simplex, 2):
        # Ordenamos los índices para que (v1, v2) y (v2, v1) colapsen en el set
        idx_min, idx_max = min(i, j), max(i, j)
        p1 = tuple(self._vertices[idx_min])
        p2 = tuple(self._vertices[idx_max])
        unique_edges.add((p1, p2))   
            
    return list(unique_edges)

  def get_boundaries(self):
    return

  def get_halfspaces(self) -> list[Halfspace]:
    if self._halfspaces is None:
      self._halfspaces = []
      TOL = 1e-8 
      
      for i in range(len(self._b)):
        normal = self._A[i]
        offset = self._b[i]
        
        # 1. Buscamos qué vértices pertenecen a esta inecuación
        distances = np.dot(self._vertices, normal) - offset
        in_plane_indices = np.where(np.isclose(distances, 0.0, atol=TOL))[0]
        
        # 2. Extraemos los vértices en tuplas puras
        extracted_points = [
            (float(self._vertices[idx][0]), float(self._vertices[idx][1])) 
            for idx in in_plane_indices
        ]
        
        # 3. Orientación geométrica y limpieza de colineales
        if len(extracted_points) >= 2:
            r = extracted_points[0]
            s = extracted_points[-1] # Garantiza agarrar los dos extremos
            
            dx = s[0] - r[0]
            dy = s[1] - r[1]
            nx, ny = normal[0], normal[1]
            
            # Producto cruzado 2D: verifica si el interior quedó a la derecha
            if nx * dy - ny * dx < 0:
                face_points = [s, r] # Invertimos para corregir la línea dirigida
            else:
                face_points = [r, s]
        else:
            face_points = extracted_points
        
        # 4. Instanciamos inyectando TODOS los datos
        hs = Halfspace(points=face_points, normalVector=normal, b=offset)
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
    poly = pc.Polytope(self._A, self._b)
    poly = pc.reduce(poly)
    self._A, self._b = poly.A, poly.b

  def get_centroid(self) -> 'Point':
    # retorna el centroide del politopo
    if self._centroid is None:
      centroidCoords = np.mean(self._vertices, axis=0)
      self._centroid = tuple(float(c) for c in centroidCoords)
    return self._centroid