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