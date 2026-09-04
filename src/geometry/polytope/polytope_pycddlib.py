from abc import ABC, abstractmethod
import numpy as np
from typing import Optional
from .polytope import Polytope
from scipy.spatial import ConvexHull
from geometry import AbstractPoint, AbstractHalfspace
import cdd
import cdd.gmp
from fractions import Fraction

class PolytopeCdd(Polytope):
  # implementación de politopos usando la librería pycddlib
  polytope: cdd.gmp.Polyhedron

  def __init__(self, 
               vertices: Optional['tuple[AbstractPoint, ...]'] = None, 
               A: Optional['np.ndarray'] = None, 
               b: Optional['np.ndarray'] = None):
    # límite para el denominador?
    if A is not None and b is not None and vertices is None: # H-rep
      b_flat = np.atleast_1d(b.squeeze())
      cdd_data = [] 
      for i in range(len(b_flat)):
        row = [Fraction(float(b_flat[i]))]
        for j in range(A.shape[1]):
          val = Fraction(float(-A[i, j]))
          row.append(val)
        cdd_data.append(row)
      mat = cdd.gmp.matrix_from_array(cdd_data, rep_type=cdd.RepType.INEQUALITY)
      self.polytope = cdd.gmp.Polyhedron(mat)

    elif A is None and b is None and vertices is not None and len(vertices) > 2: # V-rep
      pointsArray = np.array([list(v.get_point()) for v in vertices])
      cdd_data = []
      for i in range(pointsArray.shape[0]):
        row = [Fraction(1, 1)] 
        for j in range(pointsArray.shape[1]):
          val = Fraction(float(pointsArray[i, j]))
          row.append(val)
        cdd_data.append(row)
      mat = cdd.gmp.matrix_from_array(cdd_data, rep_type=cdd.RepType.GENERATOR)
      self.polytope = cdd.gmp.Polyhedron(mat)  
        
    else:
      raise ValueError("Inicialización inválida: Proveer vértices o (A, b)")
    
  def get_vertices(self) -> np.ndarray:
    # permite obtener los vértices del politopo
    generadores = cdd.gmp.copy_generators(self.polytope)
    vertices = []
    for row in generadores:
      if row[0] == 1:
        punto = [float(val) for val in row[1:]]
        vertices.append(punto)
    return np.array(vertices)
  
  def get_hrep(self) -> tuple[np.ndarray, np.ndarray]:
    # permite obtener las matrices A y b que definen al politopo
    inecuaciones = cdd.gmp.copy_inequalities(self.polytope)
    A_list = []
    b_list = []
    for row in inecuaciones:
        # El formato que nos da es [b, -A1, -A2, ...]
        b_val = float(row[0])
        b_list.append(b_val)
        A_row = [-float(val) for val in row[1:]]
        A_list.append(A_row)
    return np.array(A_list), np.array(b_list)

  def get_vertices_fraction(self) -> np.ndarray:
    # permite obtener los vértices del politopo en tipo Fraction
    generadores = cdd.gmp.copy_generators(self.polytope)
    vertices = []
    for row in generadores:
      if row[0] == 1:
        punto = [val for val in row[1:]]
        vertices.append(punto)
    return np.array(vertices)

  def _polytope_to_hrep_fraction(self, p: cdd.gmp.Polyhedron) -> tuple[np.ndarray, np.ndarray]:
    # permite obtener las matrices A y b que definen un politopo en tipo Fraction
    inecuaciones = cdd.gmp.copy_inequalities(self.polytope)
    A_list = []
    b_list = []
    for row in inecuaciones:
        # El formato que nos da es [b, -A1, -A2, ...]
        b_val = row[0]
        b_list.append(b_val)
        A_row = [-val for val in row[1:]]
        A_list.append(A_row)
    return np.array(A_list), np.array(b_list)

  def get_hrep_fraction(self) -> tuple[np.ndarray, np.ndarray]:
    # permite obtener las matrices A y b que definen al politopo en tipo Fraction
    return self._polytope_to_hrep_fraction(self.polytope)

  def _map_polytopes_from_pc(self, pcList: list[cdd.gmp.Polyhedron]) -> list['PolytopeCdd']:
    # toma una lista de cdd.gmp.Polyhedron y retorna una de PolytopeImp
    polyList = []
    for p in pcList:
      A, b = self.get_hrep_fraction() # VER CÓMO HAGO ESTO
      polyList.append(PolytopeCdd(A = A, b = b))
    return polyList

  def intersect(self, p: 'PolytopeCdd') -> list['PolytopeCdd']:
    # permite intersecar el politopo con otro
    mat1 = cdd.gmp.copy_inequalities(self.polytope)
    mat2 = cdd.gmp.copy_inequalities(p.polytope)
    cdd.gmp.matrix_append_to(mat1, mat2)
    cdd.gmp.matrix_canonicalize(mat1) # limpia inecuaciones redundantes
    intPoly = cdd.gmp.Polyhedron(mat1)
    resultado = self.__class__.__new__(self.__class__)
    resultado.polytope = intPoly
    return [resultado]

  def union(self, p: 'PolytopeCdd') -> list['PolytopeCdd']:
    # permite calcular la unión del politopo con otro
    # retorna una lista por si la región resultante no es convexa
    pass

  def difference(self, p: 'PolytopeCdd') -> list['PolytopeCdd']:
    # permite calcular la diferencia entre dos politopos
    pass

  def is_empty(self) -> bool:
    # retorna si el politopo es vacío
    verticesMatrix = cdd.gmp.copy_generators(self.polytope)
    for row in verticesMatrix:
      if row[0] == 1: # encontramos un vértice
        return False
    return True

  def _poly_contains_point(self, p: cdd.gmp.Polyhedron, x: tuple[Fraction, ...]) -> bool:
    ineq = cdd.gmp.copy_inequalities(p) # H-rep en formato [b, -A1, -A2...]
    for row in ineq:
      # if b - Ax = b + mAx >= 0 el punto pertenece
      b = row[0]
      mA = row[1:]
      res = b
      for i in range(len(x)):
        res += mA[i] * x[i]
      if res < 0:
        return False
    return True

  def contains(self, x: AbstractPoint) -> bool:
    # retorna si un punto pertenece al politopo
    point = x.get_point()
    pointFraction = tuple(Fraction(float(p)) for p in point)
    return self._poly_contains_point(self.polytope, pointFraction)

  def subset(self, p: 'PolytopeCdd') -> bool:
    # retorna si el politopo es subconjunto de p
    vertices = cdd.gmp.copy_generators(self.polytope)
    for v in vertices:
      if v[0] == 1:
        coords = v[1:]
        if not self._poly_contains_point(p.polytope, coords):
          return False
    return True

  def reduce(self):
    # elimina las inecuaciones redundantes
    ineq = cdd.gmp.copy_inequalities(self.polytope)
    noRed = cdd.gmp.matrix_canonicalize(ineq) # limpia inecuaciones redundantes
    self.polytope = cdd.gmp.Polyhedron(noRed)
