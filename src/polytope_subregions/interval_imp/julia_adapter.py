import numpy as np
from juliacall import Main as jl
jl.include("interval_main.jl")

# adaptador para convertir datos python a los que necesita julia y viceversa

_to_int_vec = jl.seval("x -> interval.(x)")
_to_int_mat = jl.seval("x -> IntervalMatrix(interval.(x))")
_get_inf_vec = jl.seval("x -> inf.(x)")
_get_mid_mat = jl.seval("x -> Matrix(mid.(x))")

## Traducción de Python a Julia

def np_to_interval_vector(arr: np.ndarray):
  # convierte un vector de numpy a un Vector{Interval}
  return _to_int_vec(arr)

def np_to_interval_matrix(mat: np.ndarray):
  # convierte una matriz de numpy a una InteralMatrix
  return _to_int_mat(mat)

## Traducción de Julia a Python

def interval_to_np_vector(jlVector) -> np.ndarray:
  # Extrae el supremo de cada elemento de un vector de intervalos
  return np.array(_get_inf_vec(jlVector))

def interval_to_np_matrix(jlMatrix) -> np.ndarray:
  return np.array(_get_mid_mat(jlMatrix))

def set_approx_method(methodName: str):
  # crea y retorna una instancia del método de aproximación deseado
  dict = {"Euler": jl.Euler, "Taylor": jl.Taylor}
  return dict[methodName]

def get_subregion_from_julia(methodName: str,
                             H: np.ndarray,
                             c: np.ndarray,
                             A: np.ndarray,
                             b: np.ndarray,
                             h: float,
                             K: int):
  # ejecuta get_subregion de Julia y retorna las matrices del politopo en formato np
  H_jl = np_to_interval_matrix(H)
  c_jl = np_to_interval_vector(c)
  A_jl = np_to_interval_matrix(A)
  b_jl = np_to_interval_vector(b)
  approx = set_approx_method(methodName)
  subregionA_jl, subregionb_jl = jl.get_subregion(approx, H_jl, c_jl, A_jl, b_jl, h, K)
  subregionA = interval_to_np_matrix(subregionA_jl)
  subregionb = interval_to_np_vector(subregionb_jl)
  return subregionA, subregionb
