import numpy as np
from juliacall import Main as jl

# adaptador para convertir datos python a los que necesita julia y viceversa

## Traducción de Python a Julia

def np_to_interval_vector(arr: np.ndarray):
  # convierte un vector de numpy a un Vector{Interval}
  return jl.seval("x -> interval.(x)")

def np_to_interval_matrix(mat: np.ndarray):
  # convierte una matriz de numpy a una InteralMatrix
  return jl.seval("x -> IntervalMatrix(interval.(x))")

## Traducción de Julia a Python

def interval_to_np_vector(jlVector) -> np.ndarray:
  # Extrae el supremo de cada elemento de un vector de intervalos
  return np.array(jl.sup(jlVector))

def interval_to_np_matrix(jlMatrix) -> np.ndarray:
  return np.array(jl.Matrix(jl.sup(jlMatrix))) # por qué Gemini dice mid y no sup?