import polytope as pc
import numpy as np
from affine_system import AffineMode

def sas_augmented_matrix(subsystem: AffineMode) -> np.ndarray:
  # dadas las matrices A y b que definen al sistema afín conmutado (SAS), calcula la matriz aumentada A tilde
  # toma el sistema en un modo particular
  A, b = subsystem.get_subsystem()
  n = A.shape[0] # dimensiones del sistema
  b = b.reshape(n, 1) # asegurar que b sea un vector columna n x 1
  zeros = np.zeros((1, n))  # fila de n ceros (0_{1xn})
  return np.block([ # matriz A tilde (homA)
      [A,     b],
      [zeros, 0]
  ])

def polytope_augmented_matrix(polytope: pc.Polytope) -> np.ndarray:
  # dado el politopo Hx <= c calcula la matriz aumentada H tilde
  H = polytope.A
  c = polytope.b
  n = H.shape[0]
  c = c.reshape(n, 1) 
  return np.hstack((H, -c)) # matriz H tilde (homH)

def partition_matrices(polytope: pc.Polytope, subsystem: AffineMode, r: float, h: float, midErrorBound: float) -> tuple[np.ndarray]:
  homA = sas_augmented_matrix(subsystem)
  homH = polytope_augmented_matrix(polytope)

  dim = homA.shape[0]
  I = np.eye(dim, dtype=np.float64)
  dim = homH.shape[0]
  ones = np.ones((dim, 1), dtype=np.float64)

  posH = np.block([
      homH,
      homH @ (I + h/2 * homA)
  ])
  
  negH = np.block([
        homH,
        homH @ (I + h/2 * homA)
    ])

  c = np.block([
        -r * ones,
        -midErrorBound * ones
    ])
  
  return posH, negH, c
  