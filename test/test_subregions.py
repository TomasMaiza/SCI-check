from src.polytope_subregions import *
from src.polytope_subregions.approximations import *
from src.affine_system import *
from numpy.testing import assert_array_equal, assert_allclose
import numpy as np
import polytope as pc
import math
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
  # test_error_sequence()

def test_euler_get_M():
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

def test_euler_error_bound():
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

def test_euler_get_matrix():
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

def test_euler_apply():
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

def test_euler_error_sequence():
    # Politopo Caja [-1, 1] x [-1, 1]
    A_poly = np.array([[ 1.0,  0.0], 
                       [-1.0,  0.0], 
                       [ 0.0,  1.0], 
                       [ 0.0, -1.0]])
    b_poly = np.array([1.0, 1.0, 1.0, 1.0]).reshape(-1, 1)
    poly_dummy = pc.Polytope(A_poly, b_poly)

    # ---------------------------------------------------------
    # Caso 1: Sistema con A nula (normA = 0, M_i = 0)
    # ---------------------------------------------------------
    A_zero = np.zeros((2, 2))
    b_zero = np.zeros((2, 1))
    mode_zero = AffineMode(A_zero, b_zero)
    euler_zero = Euler(mode_zero, poly_dummy)
    
    h_1 = 0.1
    K_1 = 3
    seq_zero = euler_zero.error_sequence(h_1, K_1)
    
    assert len(seq_zero) == K_1 + 1, "Caso 1: La secuencia debe tener K + 1 elementos"
    assert all(math.isclose(r, 0.0) for r in seq_zero), "Caso 1: Para un sistema nulo, el error debe ser 0.0 en todos los pasos"

    # ---------------------------------------------------------
    # Caso 2: Sistema con A identidad (normA = 1) para cálculo manual
    # ---------------------------------------------------------
    A_id = np.eye(2)
    b_id = np.zeros((2, 1))
    mode_id = AffineMode(A_id, b_id)
    euler_id = Euler(mode_id, poly_dummy)
    
    h_2 = 0.5
    K_2 = 2
    seq_id = euler_id.error_sequence(h_2, K_2)
    
    # Cálculo manual esperado
    # normA = 1.0. 
    # El vértice más lejano en la caja [-1, 1]x[-1, 1] tiene norma 2 igual a sqrt(2).
    # M_i = max ||Ax+b|| / ||A|| = sqrt(2) / 1.0 = sqrt(2)
    normA = 1.0
    M_i = math.sqrt(2)
    tau = abs(h_2)
    
    r0 = 0.0
    term_exp = math.exp(normA * tau) - 1 - normA * tau
    
    # r_{k+1} = r_k * (1 + normA*tau) + M_i * term_exp
    r1 = r0 * (1 + normA * tau) + M_i * term_exp
    r2 = r1 * (1 + normA * tau) + M_i * term_exp
    expected_seq_id = [r0, r1, r2]
    
    assert len(seq_id) == K_2 + 1, "Caso 2: Longitud de secuencia incorrecta"
    for r_calc, r_exp in zip(seq_id, expected_seq_id):
        assert math.isclose(r_calc, r_exp, rel_tol=1e-9), f"Caso 2: Falló el cálculo recursivo. Esperado: {r_exp}, Obtenido: {r_calc}"

    # ---------------------------------------------------------
    # Caso 3: Validación de abs(h) y crecimiento monótono
    # ---------------------------------------------------------
    h_3 = -0.2  # Paso negativo
    K_3 = 5
    seq_neg = euler_id.error_sequence(h_3, K_3)
    seq_pos = euler_id.error_sequence(abs(h_3), K_3)
    
    # Validar que ingresar -h es exactamente igual a ingresar +h
    for r_neg, r_pos in zip(seq_neg, seq_pos):
        assert math.isclose(r_neg, r_pos, rel_tol=1e-9), "Caso 3: El método no está aplicando abs(h) de forma correcta"
    
    # Validar que el error siempre crezca a medida que k avanza
    assert all(seq_pos[i] < seq_pos[i+1] for i in range(len(seq_pos)-1)), "Caso 3: El error acumulado debe crecer estrictamente en cada paso"

def test_taylor():
  pass
  # test_get_M()
  # test_error_bound()
  # test_get_matrix()
  # test_apply()
  # test_error_sequence()

def test_taylor_error_bound():
  # 1. Setup Polytope (Caja [-1, 1] x [-1, 1])
    A_poly = np.array([[ 1.0,  0.0], 
                       [-1.0,  0.0], 
                       [ 0.0,  1.0], 
                       [ 0.0, -1.0]])
    b_poly = np.array([[1.0], [1.0], [1.0], [1.0]])
    test_poly = pc.Polytope(A_poly, b_poly)
    
    # Parámetros de Taylor (arbitrarios para este test porque error_bound no los usa directamente)
    scaling = 10
    order = 4

    # ---------------------------------------------------------
    # Caso 1 y 2: Sistema con A identidad (normA = 1)
    # ---------------------------------------------------------
    A_id = np.eye(2)
    b_id = np.zeros((2, 1))
    mode_id = AffineMode(A_id, b_id)
    taylor_id = Taylor(mode_id, test_poly, scaling, order)
    
    # Calculamos M_i manualmente: max ||Ix + 0||_2 / ||I||_2 = sqrt(2) / 1.0 = sqrt(2)
    normA_id = 1.0
    M_i = math.sqrt(2)
    
    # Prueba 1: r = 0.0 (Primer paso)
    r_1 = 0.0
    tau_1 = 0.5
    expected_1 = r_1 * (1 + normA_id * tau_1) + M_i * (math.exp(normA_id * tau_1) - 1 - normA_id * tau_1)
    calc_1 = taylor_id.error_bound(r_1, tau_1)
    
    assert math.isclose(calc_1, expected_1, rel_tol=1e-9), f"Falla Prueba 1. Esperado: {expected_1}, Obtenido: {calc_1}"

    # Prueba 2: r > 0 (Pasos intermedios, el error arrastrado afecta el resultado)
    r_2 = 0.1
    tau_2 = 0.2
    expected_2 = r_2 * (1 + normA_id * tau_2) + M_i * (math.exp(normA_id * tau_2) - 1 - normA_id * tau_2)
    calc_2 = taylor_id.error_bound(r_2, tau_2)
    
    assert math.isclose(calc_2, expected_2, rel_tol=1e-9), f"Falla Prueba 2. Esperado: {expected_2}, Obtenido: {calc_2}"

    # ---------------------------------------------------------
    # Caso 3: Matriz Nula (normA = 0)
    # ---------------------------------------------------------
    A_zero = np.zeros((2, 2))
    b_zero = np.zeros((2, 1))
    mode_zero = AffineMode(A_zero, b_zero)
    taylor_zero = Taylor(mode_zero, test_poly, scaling, order)
    
    # Prueba 3: Con A = 0, la fórmula colapsa a: r * (1 + 0) + M * (1 - 1 - 0) = r
    r_3 = 1.5
    tau_3 = 0.5
    expected_3 = r_3 # El error no crece si no hay dinámica
    calc_3 = taylor_zero.error_bound(r_3, tau_3)
    
    assert math.isclose(calc_3, expected_3, rel_tol=1e-9), f"Falla Prueba 3. Esperado: {expected_3}, Obtenido: {calc_3}"

def test_taylor_get_matrix():
  # 1. Setup Polytope (Caja [-1, 1] x [-1, 1])
    A_poly = np.array([[ 1.0,  0.0], 
                       [-1.0,  0.0], 
                       [ 0.0,  1.0], 
                       [ 0.0, -1.0]])
    b_poly = np.array([[1.0], [1.0], [1.0], [1.0]])
    test_poly = pc.Polytope(A_poly, b_poly)

    # ---------------------------------------------------------
    # Caso 1: Sistema con dinámica nula (A=0, b=0)
    # ---------------------------------------------------------
    A_zero = np.zeros((2, 2))
    b_zero = np.zeros((2, 1))
    mode_zero = AffineMode(A_zero, b_zero)
    taylor_zero = Taylor(mode_zero, test_poly, scaling=5, order=4)
    
    h_1 = 0.5
    calc_Phi_zero = taylor_zero.get_matrix(h_1)
    
    # Si la dinámica es 0, la transición de estado es la matriz Identidad
    expected_Phi_zero = np.eye(3)
    assert_allclose(calc_Phi_zero, expected_Phi_zero, rtol=1e-9, atol=1e-9,
                    err_msg="Falla Caso 1: La matriz para un sistema nulo debe ser la Identidad 3x3")

    # ---------------------------------------------------------
    # Caso 2: Colapso a Euler (M=1, s=1)
    # ---------------------------------------------------------
    A_id = np.eye(2)
    b_id = np.array([[1.0], [2.0]])
    mode_id = AffineMode(A_id, b_id)
    taylor_euler = Taylor(mode_id, test_poly, scaling=1, order=1)
    
    h_2 = 0.2
    homA_id = np.array([[1.0, 0.0, 1.0], 
                        [0.0, 1.0, 2.0], 
                        [0.0, 0.0, 0.0]])
    
    calc_Phi_euler = taylor_euler.get_matrix(h_2)
    expected_Phi_euler = np.eye(3) + homA_id * h_2
    
    assert_allclose(calc_Phi_euler, expected_Phi_euler, rtol=1e-9, atol=1e-9,
                    err_msg="Falla Caso 2: Con M=1 y s=1, el resultado debe ser igual a (I + A_tilde * h)")

    # ---------------------------------------------------------
    # Caso 3: Matriz Nilpotente (A^2 = 0)
    # ---------------------------------------------------------
    # Para A = [0 1; 0 0], homA al cuadrado es una matriz de ceros.
    A_nil = np.array([[0.0, 1.0], 
                      [0.0, 0.0]])
    b_nil = np.array([[1.0], 
                      [0.0]])
    mode_nil = AffineMode(A_nil, b_nil)
    
    # Usamos valores altos de M y s, el resultado debe ser matemáticamente exacto igual
    taylor_nil = Taylor(mode_nil, test_poly, scaling=8, order=5)
    
    h_3 = 0.5
    homA_nil = np.array([[0.0, 1.0, 1.0], 
                         [0.0, 0.0, 0.0], 
                         [0.0, 0.0, 0.0]])
    
    calc_Phi_nil = taylor_nil.get_matrix(h_3)
    # Como homA^2 = 0, la serie de Taylor (y expm) es exactamente I + homA * h
    expected_Phi_nil = np.eye(3) + homA_nil * h_3
    
    assert_allclose(calc_Phi_nil, expected_Phi_nil, rtol=1e-9, atol=1e-9,
                    err_msg="Falla Caso 3: Para matriz nilpotente, la aproximación se rompió por el escalado")

def test_taylor_error_sequence():
  # 1. Setup Polytope (Caja [-1, 1] x [-1, 1])
    # Su R_S será la norma de [1, 1, 1] = sqrt(1^2 + 1^2 + 1^2) = sqrt(3)
    A_poly = np.array([[ 1.0,  0.0], 
                       [-1.0,  0.0], 
                       [ 0.0,  1.0], 
                       [ 0.0, -1.0]])
    b_poly = np.array([[1.0], [1.0], [1.0], [1.0]])
    test_poly = pc.Polytope(A_poly, b_poly)

    # ---------------------------------------------------------
    # Caso 1: Dinámica Nula (A=0, b=0)
    # ---------------------------------------------------------
    A_zero = np.zeros((2, 2))
    b_zero = np.zeros((2, 1))
    mode_zero = AffineMode(A_zero, b_zero)
    taylor_zero = Taylor(mode_zero, test_poly, scaling=10, order=4)
    
    K_1 = 3
    h_1 = 0.1
    seq_zero = taylor_zero.error_sequence(h_1, K_1)
    
    assert len(seq_zero) == K_1 + 1, "Caso 1: La secuencia debe tener K + 1 elementos."
    assert all(math.isclose(r, 0.0) for r in seq_zero), "Caso 1: Si la dinámica es nula, el error de Taylor debe ser exactamente 0.0 en todo k."

    # ---------------------------------------------------------
    # Caso 2: Validación matemática exacta con A=Identidad
    # ---------------------------------------------------------
    A_id = np.eye(2)
    b_id = np.zeros((2, 1))
    mode_id = AffineMode(A_id, b_id)
    
    s = 2
    M = 2
    taylor_id = Taylor(mode_id, test_poly, scaling=s, order=M)
    
    K_2 = 2
    h_2 = 0.5
    seq_id = taylor_id.error_sequence(h_2, K_2)
    
    # --- Cálculo Manual ---
    # normHomA es la norma 2 de diag(1, 1, 0) = 1.0
    normHomA = 1.0 
    R_S = math.sqrt(3.0) 
    
    # C_err = ((h * normHomA)**(M+1) * R_S) / (s**M * factorial(M+1))
    num = (h_2 * normHomA)**(M + 1) * R_S
    den = (s**M) * math.factorial(M + 1)
    C_err_manual = num / den
    
    expected_seq = []
    for k in range(K_2 + 1):
        r_k = k * C_err_manual * math.exp(normHomA * h_2 * k)
        expected_seq.append(r_k)
        
    assert len(seq_id) == K_2 + 1, "Caso 2: Longitud incorrecta."
    for calc, exp in zip(seq_id, expected_seq):
        assert math.isclose(calc, exp, rel_tol=1e-9), f"Caso 2: Falla el cálculo en la secuencia. Esperado: {exp}, Obtenido: {calc}"

    # ---------------------------------------------------------
    # Caso 3: La condición inicial siempre es 0
    # ---------------------------------------------------------
    assert math.isclose(seq_id[0], 0.0, abs_tol=1e-12), "Caso 3: El error inicial en k=0 siempre debe ser 0 para no encoger la región inicial."

def test_subregions():
  pass
  # test_create_halfspaces_list()
  # test_get_subregion()
  # test_get_subregions()

def test_create_halfspaces_list():
  geometry_2d = GeometryFactory[2]()
  subregions = Subregions(geometry=geometry_2d)
    
  # 2. Setup del politopo de prueba
  A_poly = np.array([[ 1.0,  0.0], 
                     [-1.0,  0.0], 
                     [ 0.0,  1.0], 
                     [ 0.0, -1.0]])
                       
  b_poly = np.array([[1.0], 
                     [2.0], 
                     [3.0], 
                     [4.0]]) 
                       
  test_poly = pc.Polytope(A_poly, b_poly)
    
  # 3. Ejecución del método
  halfspaces = subregions._create_halfspaces_list(test_poly)
    
  # 4. Validaciones
  assert len(halfspaces) == 4, "Debe retornar exactamente 4 semiespacios."
    
  # Validamos arista por arista de forma independiente del índice
  for hs in halfspaces:
    p1_coord = np.array([hs.p1.x, hs.p1.y])
    p2_coord = np.array([hs.p2.x, hs.p2.y])
    
    found_matching_hyperplane = False
    
    # Buscamos en qué cara del politopo original encajan estos dos puntos
    for j in range(len(A_poly)):
        A_row = A_poly[j]
        b_val = float(b_poly[j][0])
        
        # Evaluamos si ambos puntos cumplen la ecuación de la recta de esta cara
        p1_on_line = np.isclose(np.dot(A_row, p1_coord), b_val, rtol=1e-5, atol=1e-8)
        p2_on_line = np.isclose(np.dot(A_row, p2_coord), b_val, rtol=1e-5, atol=1e-8)
        
        if p1_on_line and p2_on_line:
            found_matching_hyperplane = True
            break # Encontramos la cara correcta, no hace falta seguir buscando
            
    assert found_matching_hyperplane, (
        f"El semiespacio formado por p1={p1_coord} y p2={p2_coord} "
        f"no corresponde a ninguna de las caras del politopo original."
    )

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

  # CASO 2: Sistema dinámico con deriva constante (Drift)
  # A nula, pero el sistema se mueve a la derecha a 0.5 unidades/seg
  A_sys_drift = np.array([[0.0, 0.0], 
                            [0.0, 0.0]])
  b_sys_drift = np.array([[0.5], 
                            [0.0]])
  drift_subsystem = AffineMode(A_sys_drift, b_sys_drift)

  K_steps_drift = 1
  h_step_drift = 1.0 # 1 segundo entero para que el desplazamiento sea notorio
    
  halfspaces_drift = subregions.get_subregion(
        subsystem=drift_subsystem, 
        polytope=test_poly, # Reutilizamos la caja de [-1, 1]
        K=K_steps_drift, 
        h=h_step_drift
    )
    
  # Validaciones básicas
  assert isinstance(halfspaces_drift, list), "Debe retornar una lista."
  assert len(halfspaces_drift) > 0, "El politopo recortado no debe estar vacío."
    
  for i, hs in enumerate(halfspaces_drift):
    assert hasattr(hs, 'p1') and hasattr(hs, 'p2'), "Faltan los puntos geométricos."
    assert hs.p1 is not None and hs.p2 is not None, "Los puntos no pueden ser nulos."

  # Validación geométrica avanzada (opcional pero recomendada):
  # Como el politopo se tuvo que haber recortado, es muy probable que 
  # la cantidad de semiespacios haya cambiado o que las inecuaciones 
  # resultantes (luego de pc.reduce) reflejen el nuevo límite en x <= 0.5.
  print(f"\nCaso estático generó {len(halfspaces)} semiespacios.")
  print(f"Caso con deriva generó {len(halfspaces_drift)} semiespacios.")

  # CASO 3: Sistema contractivo (Estable) con A y b no nulos
  # Matriz A con autovalores negativos (-0.5 y -1.5) que atrae al estado.
  # Los términos cruzados (0.5) prueban que x e y interactúen bien.
  A_sys_stable = np.array([[-1.0,  0.5], 
                             [ 0.5, -1.0]])
                             
  # Deriva leve que desplaza el punto de equilibrio fuera del origen
  b_sys_stable = np.array([[ 0.1], 
                             [-0.1]])
                             
  stable_subsystem = AffineMode(A_sys_stable, b_sys_stable)

  # Le damos 5 pasos enteros de propagación hacia el futuro
  K_steps_stable = 5  
  h_step_stable = 0.1 
    
  # Esta es la prueba definitiva de la propagación del error y la 
  # acumulación de matrices Phi_k a lo largo del tiempo.
  halfspaces_stable = subregions.get_subregion(
        subsystem=stable_subsystem, 
        polytope=test_poly, # Seguimos usando la caja centrada de [-1, 1]
        K=K_steps_stable, 
        h=h_step_stable
    )
    
  # Validaciones 
  assert isinstance(halfspaces_stable, list), "Debe retornar una lista."
  assert len(halfspaces_stable) > 0, "El politopo contractivo no debe estar vacío."
    
  for i, hs in enumerate(halfspaces_stable):
    assert hasattr(hs, 'p1') and hasattr(hs, 'p2'), "Faltan los puntos geométricos."
    assert hs.p1 is not None and hs.p2 is not None, "Los puntos no pueden ser nulos."

def test_get_subregions():
  geometry_2d = GeometryFactory[2]()
  subregions = Subregions(geometry=geometry_2d)
    
  # Caja inicial de [-1, 1]
  A_poly = np.array([[ 1.0,  0.0], [-1.0,  0.0], [ 0.0,  1.0], [ 0.0, -1.0]])
  b_poly = np.array([[1.0], [1.0], [1.0], [1.0]]) 
  test_poly = pc.Polytope(A_poly, b_poly)

  # 2. Configuración de matrices para los modos
  # Modo 0: Sistema estático (sin dinámica)
  A_static = np.zeros((2, 2))
  b_static = np.zeros((2, 1))
    
  # Modo 1: Sistema con deriva constante
  A_drift = np.zeros((2, 2))
  b_drift = np.array([[0.5], [0.0]])

  # 3. Instanciamos el SwitchedAffineSystem REAL
  modes_dict = {
    0: (A_static, b_static),
    1: (A_drift, b_drift)
  }
  real_sas = SwitchedAffineSystem(modes_dict)

  # 4. Ejecución del orquestador principal
  dwell_time = 1.0
  K_steps = 2
    
  polytope_list = subregions.get_subregions(
        sas=real_sas, 
        polytope=test_poly, 
        dwellTime=dwell_time, 
        K=K_steps
    )
    
  # 5. Validaciones estructurales y geométricas
  assert isinstance(polytope_list, list), "Debe retornar una lista."
  assert len(polytope_list) == 2, "Debe contener subregiones para exactamente 2 modos."
    
  # Validamos el acceso directo por índice (0 y 1)
  for i in range(len(polytope_list)):
    halfspaces = polytope_list[i]
    assert isinstance(halfspaces, list), f"El valor en el índice {i} debe ser una lista."
    assert len(halfspaces) > 0, f"El politopo resultante para el modo {i} está vacío."
    assert hasattr(halfspaces[0], 'p1'), "Los elementos de la lista deben ser semiespacios válidos."