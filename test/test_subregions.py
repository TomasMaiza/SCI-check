from src.polytope_subregions import *
from src.polytope_subregions.approximations import *
from src.affine_system import *
from numpy.testing import assert_array_equal, assert_allclose
import numpy as np
import polytope as pc
from src.geometry import GeometryFactory, AbstractHalfspace

def test_matrices():
  pass
  # test_sas_augmented_matrix()
  # test_polytope_augmented_matrix()
  # test_partition_matrices()

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
  pass
  # test_get_M()
  # test_error_bound()
  # test_get_matrix()
  # test_apply()

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

def test_get_matrix():
  A_poly = np.array([[ 1.0,  0.0], 
                       [-1.0,  0.0], 
                       [ 0.0,  1.0], 
                       [ 0.0, -1.0]])
  b_poly = np.array([1.0, 1.0, 1.0, 1.0]).reshape(-1, 1)
  poly_dummy = pc.Polytope(A_poly, b_poly)

  A_sys = np.array([[2.0, 0.0], 
                      [0.0, 2.0]])
  b_sys = np.array([[1.0], 
                      [0.0]])
  mode_sys = AffineMode(A_sys, b_sys)
  euler_sys = Euler(mode_sys, poly_dummy)

  # Caso 1: s = 0.0 (Debe devolver la matriz Identidad)
  dim = euler_sys._homA.shape[0]
  expected_identity = np.eye(dim, dtype=np.float64)
    
  result_zero = euler_sys.get_matrix(s=0.0)
    
  assert_allclose(result_zero, expected_identity, rtol=1e-5, atol=1e-8,
                    err_msg="Si s=0, la matriz de aproximación debe ser exactamente la Identidad.")

  # Caso 2: s > 0 (Aproximación de Euler estándar)
  s_val = 0.1
    
  # MATEMÁTICA DEL TEST:
  # homA teórica esperada para A_sys y b_sys:
  # [[2.0, 0.0, 1.0],
  #  [0.0, 2.0, 0.0],
  #  [0.0, 0.0, 0.0]]
  #
  # I + 0.1 * homA debería dar como resultado:
  expected_matrix = np.array([
        [1.2, 0.0, 0.1],
        [0.0, 1.2, 0.0],
        [0.0, 0.0, 1.0]
  ], dtype=np.float64)
    
  result_s = euler_sys.get_matrix(s=s_val)
    
  assert_allclose(result_s, expected_matrix, rtol=1e-5, atol=1e-8,
                    err_msg="La matriz aproximada no coincide con el cálculo I + s*homA.")
  
  # Caso 3: s < 0 (Aproximación con flujo temporal negativo)
  s_neg = -0.1
    
  # I - 0.1 * homA
  expected_matrix_neg = np.array([
        [0.8, 0.0, -0.1],
        [0.0, 0.8,  0.0],
        [0.0, 0.0,  1.0]
  ], dtype=np.float64)
    
  result_neg = euler_sys.get_matrix(s=s_neg)
    
  assert_allclose(result_neg, expected_matrix_neg, rtol=1e-5, atol=1e-8,
                    err_msg="La matriz aproximada falla para valores de s negativos (s < 0).")

def test_apply():
  A_poly = np.array([[ 1.0,  0.0], 
                       [-1.0,  0.0], 
                       [ 0.0,  1.0], 
                       [ 0.0, -1.0]])
  b_poly = np.array([1.0, 1.0, 1.0, 1.0]).reshape(-1, 1)
  poly_dummy = pc.Polytope(A_poly, b_poly)

  A_sys = np.array([[2.0, 0.0], 
                      [0.0, 2.0]])
  b_sys = np.array([[1.0], 
                      [0.0]])
  mode_sys = AffineMode(A_sys, b_sys)
  euler_sys = Euler(mode_sys, poly_dummy)

  # Definimos un vector de estado de prueba estricto (columna)
  # x = [1, 1]^T
  x_val = np.array([[1.0], 
                      [1.0]])

  # Caso 1: s = 0.0 (El estado no debe cambiar)
  result_zero = euler_sys.apply(s=0.0, x=x_val)
    
  assert_allclose(result_zero, x_val, rtol=1e-5, atol=1e-8,
                    err_msg="Si s=0, la función apply debe devolver el mismo estado inicial x.")

  # Caso 2: s > 0 (Evolución hacia adelante)
  s_pos = 0.1
    
  # MATEMÁTICA DEL TEST:
  # A*x + b = [[2, 0], [0, 2]] @ [[1], [1]] + [[1], [0]] 
  #         = [[2], [2]] + [[1], [0]] = [[3], [2]]
  # x + 0.1 * [[3], [2]] = [[1], [1]] + [[0.3], [0.2]] = [[1.3], [1.2]]
  expected_pos = np.array([[1.3], 
                             [1.2]])
                             
  result_pos = euler_sys.apply(s=s_pos, x=x_val)
    
  assert_allclose(result_pos, expected_pos, rtol=1e-5, atol=1e-8,
                    err_msg="El estado calculado falla para s > 0.")

  # Caso 3: s < 0 (Evolución hacia atrás)
  s_neg = -0.1
    
  # x - 0.1 * [[3], [2]] = [[1], [1]] - [[0.3], [0.2]] = [[0.7], [0.8]]
  expected_neg = np.array([[0.7], 
                             [0.8]])
                             
  result_neg = euler_sys.apply(s=s_neg, x=x_val)
    
  assert_allclose(result_neg, expected_neg, rtol=1e-5, atol=1e-8,
                    err_msg="El estado calculado falla para s < 0.")

def test_subregions():
  pass
  # test_create_halfspaces_list()
  # test_get_subregion()

def test_create_halfspaces_list():
  geometry_2d = GeometryFactory[2]()
  subregions = Subregions(geometry=geometry_2d)
    
  # 2. Setup del politopo de prueba
  A_poly = np.array([[ 1.0,  0.0], 
                      [-1.0,  0.0], 
                      [ 0.0,  1.0], 
                      [ 0.0, -1.0]])
                       
  # Mantenemos el estándar de vector columna estricto (4, 1)
  b_poly = np.array([[1.0], 
                       [2.0], 
                       [3.0], 
                       [4.0]]) 
                       
  test_poly = pc.Polytope(A_poly, b_poly)
    
  # 3. Ejecución del método
  # Llamamos al método "protegido" para aislar su validación
  halfspaces = subregions._create_halfspaces_list(test_poly)
    
  # 4. Validaciones
  # Al inyectarle un politopo con 4 inecuaciones, debe devolver 4 objetos
  assert len(halfspaces) == 4, "Debe retornar exactamente 4 semiespacios (uno por fila de la matriz A)."
    
  for i, hs in enumerate(halfspaces):
    # Extraemos los valores originales del politopo para esta iteración
    A_row = A_poly[i]  
    b_val = float(b_poly[i][0]) 
        
    # Armamos los vectores con las coordenadas de los puntos generados
    p1_coord = np.array([hs.p1.x, hs.p1.y])
    p2_coord = np.array([hs.p2.x, hs.p2.y])
        
    # Validamos que p1 pertenece a la recta original (A_row * p1 = b_val)
    assert_allclose(np.dot(A_row, p1_coord), b_val, rtol=1e-5, atol=1e-8,
                    err_msg=f"El punto p1 del semiespacio {i} no corresponde al politopo original.")
                        
    # Validamos que p2 pertenece a la recta original (A_row * p2 = b_val)
    assert_allclose(np.dot(A_row, p2_coord), b_val, rtol=1e-5, atol=1e-8,
                    err_msg=f"El punto p2 del semiespacio {i} no corresponde al politopo original.")

def test_get_subregion():
  geometry_2d = GeometryFactory[2]()
  subregions = Subregions(geometry=geometry_2d)
    
  # Caja de [-1, 1] bien centrada
  A_poly = np.array([[ 1.0,  0.0], 
                       [-1.0,  0.0], 
                       [ 0.0,  1.0], 
                       [ 0.0, -1.0]])
  b_poly = np.array([[1.0], 
                       [1.0], 
                       [1.0], 
                       [1.0]]) 
  test_poly = pc.Polytope(A_poly, b_poly)

  # Sistema estático: A y b nulos. El estado se queda quieto.
  A_sys = np.array([[0.0, 0.0], 
                      [0.0, 0.0]])
  b_sys = np.array([[0.0], 
                      [0.0]])
  test_subsystem = AffineMode(A_sys, b_sys)

  # 2. Ejecución con K=1 para probar la iteración
  K_steps = 1
  h_step = 0.1
    
  halfspaces = subregions.get_subregion(
        subsystem=test_subsystem, 
        polytope=test_poly, 
        K=K_steps, 
        h=h_step
    )

  # 3. Validaciones estructurales
  assert isinstance(halfspaces, list), "El método debe retornar una lista."
  assert len(halfspaces) > 0, "El politopo resultante no debería estar vacío (lista vacía)."
    
  for i, hs in enumerate(halfspaces):
    assert hasattr(hs, 'p1'), f"El semiespacio {i} no tiene el atributo p1."
    assert hasattr(hs, 'p2'), f"El semiespacio {i} no tiene el atributo p2."
    assert hs.p1 is not None and hs.p2 is not None, "Los puntos del semiespacio están vacíos."