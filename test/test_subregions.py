from src.polytope_subregions import *
from src.polytope_subregions.approximations import *
from src.affine_system import *
from numpy.testing import assert_array_equal
import numpy as np
import polytope as pc

def test_matrices():
  test_sas_augmented_matrix()
  test_polytope_augmented_matrix()
  test_partition_matrices()

def test_sas_augmented_matrix():
  # Caso 1: sistema estándar 2d
  A_2d = np.array([[ 1.0, -0.5], 
                     [ 2.0,  3.0]])
  b_2d = np.array([[1.5], 
                    [-2.0]])
  mode_2d = AffineMode(A_2d, b_2d)
    
  expected_2d = np.array([
        [1.0, -0.5,  1.5],
        [2.0,  3.0, -2.0],
        [0.0,  0.0,  0.0]
  ])
    
  result_2d = sas_augmented_matrix(mode_2d)
  assert_array_equal(result_2d, expected_2d, 
                     err_msg="Falló el ensamblaje para un sistema 2D estándar")

  # Caso 2: sistema 1d

  A_1d = np.array([[-2.0]])
  b_1d = np.array([[4.0]])
  mode_1d = AffineMode(A_1d, b_1d)
    
  expected_1d = np.array([
        [-2.0, 4.0],
        [ 0.0, 0.0]
  ])
    
  result_1d = sas_augmented_matrix(mode_1d)
  assert_array_equal(result_1d, expected_1d, 
                     err_msg="Falló el ensamblaje para un sistema 1D escalar")

  # Caso 3: sistema con vector b nulo

  A_lin = np.array([[-1.0,  0.0], 
                      [ 0.0, -1.0]])
  b_lin = np.array([[0.0], 
                    [0.0]])
  mode_lin = AffineMode(A_lin, b_lin)
    
  expected_lin = np.array([
        [-1.0,  0.0, 0.0],
        [ 0.0, -1.0, 0.0],
        [ 0.0,  0.0, 0.0]
  ])
    
  result_lin = sas_augmented_matrix(mode_lin)
  assert_array_equal(result_lin, expected_lin, 
                     err_msg="Falló el ensamblaje cuando el vector b es nulo")

def test_polytope_augmented_matrix():
  # Caso 1: politopo 2d estándar (un cuadrado)
  A_box = np.array([[ 1.0,  0.0], 
                      [-1.0,  0.0], 
                      [ 0.0,  1.0], 
                      [ 0.0, -1.0]])
  b_box = np.array([[1.0], 
                      [1.0], 
                      [1.0], 
                      [1.0]])
  poly_box = pc.Polytope(A_box, b_box)
    
  expected_box = np.array([
        [ 1.0,  0.0,  -1.0],
        [-1.0,  0.0,  -1.0],
        [ 0.0,  1.0,  -1.0],
        [ 0.0, -1.0,  -1.0]
  ])
    
  result_box = polytope_augmented_matrix(poly_box)
  assert_array_equal(result_box, expected_box,
                     err_msg="Falló el ensamblaje para un politopo 2D estándar (caja)")

  # Caso 2: politopo 1d
  A_1d = np.array([[ 1.0], 
                     [-1.0]])
  b_1d = np.array([[5.0], 
                     [5.0]])
  poly_1d = pc.Polytope(A_1d, b_1d)
    
  expected_1d = np.array([
        [ 1.0, -5.0],
        [-1.0, -5.0]
  ])
    
  result_1d = polytope_augmented_matrix(poly_1d)
  assert_array_equal(result_1d, expected_1d,
                     err_msg="Falló el ensamblaje para un politopo 1D (intervalo)")

def test_partition_matrices():
  pass

def test_euler():
  pass

def test_subregions():
  pass