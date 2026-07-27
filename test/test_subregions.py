from src.polytope_subregions import *
from src.polytope_subregions.approximations import *
from src.affine_system import *
from numpy.testing import assert_array_equal, assert_allclose
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
  # Seteo politopo 2d (cuadrado)
  A_poly = np.array([[ 1.0,  0.0], 
                     [-1.0,  0.0], 
                     [ 0.0,  1.0], 
                     [ 0.0, -1.0]])
  b_poly = np.array([1.0, 1.0, 1.0, 1.0]).reshape(-1, 1) # Vector columna estricto
  polytope_region = pc.Polytope(A_poly, b_poly)
    
  # seteo subsistema afín
  A_sys = np.array([[-1.0,  0.5], 
                    [ 2.0, -2.0]])
  b_sys = np.array([0.5, -0.1]).reshape(-1, 1) # Vector columna estricto
  subsystem = AffineMode(A_sys, b_sys)
    
  # parámetros 
  r = 0.1             # Escala/radio de la subregión
  h = 0.01            # Paso de discretización
  midErrorBound = 0.05 # Cota de error
    
  # ejecución
  result = partition_matrices(polytope_region, subsystem, r, h, midErrorBound)
    
  # aserciones estructurales
  assert isinstance(result, tuple), "El resultado debe ser una tupla."
  assert len(result) > 0, "La tupla devuelta no debería estar vacía."
    
  for i, matrix in enumerate(result):
    assert isinstance(matrix, np.ndarray), f"El elemento {i} de la tupla no es un np.ndarray."
    assert not np.isnan(matrix).any(), f"La matriz {i} contiene valores NaN (posible error en la discretización)."
    assert not np.isinf(matrix).any(), f"La matriz {i} contiene valores Inf."

  # aserciones numéricas
  Hplus_actual, Hminus_actual, c_actual = result
    
  # homH superior (caja original [A, -b]) + homH @ (I + (h/2)*homA) inferior
  expected_Hplus = np.array([
        [ 1.0,    0.0,   -1.0   ],
        [-1.0,    0.0,   -1.0   ],
        [ 0.0,    1.0,   -1.0   ],
        [ 0.0,   -1.0,   -1.0   ],
        [ 0.995,  0.0025, -0.9975],
        [-0.995, -0.0025, -1.0025],
        [ 0.01,   0.99,   -1.0005],
        [-0.01,  -0.99,   -0.9995]
  ])
    
  # homH superior (caja original [A, -b]) + homH @ (I - (h/2)*homA) inferior
  expected_Hminus = np.array([
        [ 1.0,    0.0,   -1.0   ],
        [-1.0,    0.0,   -1.0   ],
        [ 0.0,    1.0,   -1.0   ],
        [ 0.0,   -1.0,   -1.0   ],
        [ 1.005, -0.0025, -1.0025],
        [-1.005,  0.0025, -0.9975],
        [-0.01,   1.01,   -0.9995],
        [ 0.01,  -1.01,   -1.0005]
  ])
    
  # Vector c: r arriba, midErrorBound abajo (esto no cambia)
  expected_c = np.array([
        [-0.10], [-0.10], [-0.10], [-0.10],
        [-0.05], [-0.05], [-0.05], [-0.05]
  ])
    
  assert_allclose(Hplus_actual, expected_Hplus, rtol=1e-5, atol=1e-8, 
                  err_msg="Hplus no coincide con los valores esperados.")
                    
  assert_allclose(Hminus_actual, expected_Hminus, rtol=1e-5, atol=1e-8, 
                  err_msg="Hminus no coincide con los valores esperados.")
                    
  assert_allclose(c_actual, expected_c, rtol=1e-5, atol=1e-8, 
                  err_msg="El vector c de cotas no coincide.")

def test_euler():
  test_get_M()
  test_error_bound()

def test_get_M():
  # Caso 1: A_i = 0 (normA < 1e-12)
  A_zero = np.zeros((2, 2))
  b_zero = np.zeros((2, 1))
  mode_zero = AffineMode(A_zero, b_zero)
    
  # Caja de [-1, 1] en X e Y
  A_poly = np.array([[ 1.0,  0.0], 
                     [-1.0,  0.0], 
                     [ 0.0,  1.0], 
                     [ 0.0, -1.0]])
  b_poly = np.array([1.0, 1.0, 1.0, 1.0]).reshape(-1, 1)
  poly_dummy = pc.Polytope(A_poly, b_poly)
    
  # Instanciamos la clase de Euler
  euler_zero = Euler(mode_zero, poly_dummy)
    
  result_zero = euler_zero._get_M(normA=0.0)
  assert result_zero == 0.0, "M_i debe ser exactamente 0.0 cuando normA < 1e-12."

  # Caso 2: A_i != 0 (Evaluación de vértices)

  # Sistema: A = [[2, 0], [0, 2]], b = [[1], [0]]
  # normA (norma 2) = 2.0
  A_sys = np.array([[2.0, 0.0], 
                    [0.0, 2.0]])
  b_sys = np.array([[1.0], 
                    [0.0]])
  mode_sys = AffineMode(A_sys, b_sys)
    
  # Usamos el mismo politopo dummy: Caja [-1, 1] x [-1, 1]
  euler_sys = Euler(mode_sys, poly_dummy)
    
  normA = np.linalg.norm(A_sys, ord=2)  # Esto es exactamente 2.0
    
  # El máximo de ||Ax + b||_2 en esa caja se da en el vértice [1, 1]^T o [1, -1]^T
  # Ax + b evaluado ahí da [3, 2]^T. Su norma 2 es sqrt(3^2 + 2^2) = sqrt(13).
  # Entonces M = sqrt(13) / normA = sqrt(13) / 2.
  expected_M = np.sqrt(13) / 2.0  
    
  result_M = euler_sys._get_M(normA=normA)
    
  assert_allclose(result_M, expected_M, rtol=1e-5, atol=1e-8,
                  err_msg="El cálculo de M_i no coincide con el máximo teórico.")

def test_error_bound():
  # Politopo Caja [-1, 1] x [-1, 1]
  A_poly = np.array([[ 1.0,  0.0], 
                       [-1.0,  0.0], 
                       [ 0.0,  1.0], 
                       [ 0.0, -1.0]])
  b_poly = np.array([1.0, 1.0, 1.0, 1.0]).reshape(-1, 1)
  poly_dummy = pc.Polytope(A_poly, b_poly)

  # Caso 1: Sistema con A nula (normA = 0, M = 0)
  A_zero = np.zeros((2, 2))
  b_zero = np.zeros((2, 1))
  mode_zero = AffineMode(A_zero, b_zero)
  euler_zero = Euler(mode_zero, poly_dummy)
    
  r_val = 0.5
  tau_val = 0.01
    
  # Si normA = 0 y M = 0, la Ec 11 colapsa a: Delta = r * (1 + 0) + 0 = r
  result_zero = euler_zero.error_bound(r=r_val, tau=tau_val)
  assert result_zero == r_val, "Si A=0, el error bound debe ser exactamente igual a r."

  # Caso 2: Sistema dinámico general
  A_sys = np.array([[2.0, 0.0], 
                      [0.0, 2.0]])
  b_sys = np.array([[1.0], 
                      [0.0]])
  mode_sys = AffineMode(A_sys, b_sys)
  euler_sys = Euler(mode_sys, poly_dummy)
    
  r_val = 0.1
  tau_val = 0.05
    
  # Valores teóricos conocidos de la prueba anterior
  normA_teorico = 2.0
  M_teorico = np.sqrt(13) / 2.0
    
  # Armamos la ecuación 11 teórica en Python puro para contrastar
  termino_1 = r_val * (1.0 + normA_teorico * tau_val)
  termino_2 = M_teorico * (np.exp(normA_teorico * tau_val) - 1.0 - normA_teorico * tau_val)
  expected_error = termino_1 + termino_2
    
  result_sys = euler_sys.error_bound(r=r_val, tau=tau_val)
    
  assert_allclose(result_sys, expected_error, rtol=1e-5, atol=1e-8,
                    err_msg="El error bound no coincide con la Ecuación 11 teórica.")

def test_subregions():
  pass