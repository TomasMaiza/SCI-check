import polytope as pc
import numpy as np

def sas_augmented_matrix(self, A: np.ndarray, b: np.ndarray) -> np.ndarray:
  # dadas las matrices A y b que definen al sistema afín conmutado (SAS), calcula la matriz aumentada A tilde
  # toma las matrices para un modo particular
  n = A.shape[0] # dimensiones del sistema
  b = b.reshape(n, 1) # asegurar que b sea un vector columna n x 1
  zeros = np.zeros((1, n))  # fila de n ceros (0_{1xn})
  return np.block([ # matriz A tilde (homA)
      [A,     b],
      [zeros, 0]
  ])

def polytope_augmented_matrix(self, polytope: pc.Polytope) -> np.ndarray:
  # dado el politopo Hx <= c calcula la matriz aumentada H tilde
  H = polytope.A
  c = polytope.b
  n = H.shape[0]
  c = c.reshape(n, 1) 
  return np.hstack((H, -c)) # matriz H tilde (homH)