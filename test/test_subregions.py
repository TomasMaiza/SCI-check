from polytope_subregions import *
from polytope_subregions.approximations import *
from affine_system import *
from numpy.testing import assert_array_equal
import numpy as np

def test_matrices():
  test_sas_augmented_matrix()

def test_euler():
  pass

def test_subregions():
  pass

def test_sas_augmented_matrix():
  # Caso 1: sistema estándar 2d
  A_2d = np.array([[ 1.0, -0.5], 
                     [ 2.0,  3.0]])
  b_2d = np.array([1.5, -2.0])
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
  b_1d = np.array([4.0])
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
  b_lin = np.array([0.0, 0.0])
  mode_lin = AffineMode(A_lin, b_lin)
    
  expected_lin = np.array([
        [-1.0,  0.0, 0.0],
        [ 0.0, -1.0, 0.0],
        [ 0.0,  0.0, 0.0]
  ])
    
  result_lin = sas_augmented_matrix(mode_lin)
  assert_array_equal(result_lin, expected_lin, 
                     err_msg="Falló el ensamblaje cuando el vector b es nulo")