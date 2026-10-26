import os

os.environ["PYTHON_JULIAPKG_EXE"] = "/home/tomi/.julia/juliaup/julia-1.13.1+0.x64.linux.gnu/bin/julia"
os.environ["PYTHON_JULIAPKG_OFFLINE"] = "yes"
os.environ["JULIA_PROJECT"] = os.path.expanduser("~/.julia/environments/v1.13")

import numpy as np
from typing import Any
from juliacall import Main as jl

script_dir = os.path.dirname(os.path.abspath(__file__))
jl.include(os.path.join(script_dir, "functions.jl"))

# adaptador para convertir datos python a los que necesita julia y viceversa

def create_polytope(vertices: np.ndarray = None, A: np.ndarray = None, b: np.ndarray = None) -> Any:
  # Retorna la referencia al objeto Polyhedron de Julia
  return jl.create_exact_polyhedron(vertices, A, b)

def get_pessimistic_hrep(jl_poly: Any) -> tuple[np.ndarray, np.ndarray]:
  # Julia devuelve la tupla (Matrix{Float64}, Vector{Float64})
  # juliacall los convierte automáticamente, pero nos aseguramos de que sean numpy arrays
  A_float, b_pesimista = jl.get_pessimistic_hrep(jl_poly)
  return np.array(A_float), np.array(b_pesimista).flatten()

def get_exact_facets(jl_poly: Any) -> list[Any]:
  # Devuelve una lista de referencias a sub-poliedros de Julia
  return list(jl.get_exact_facets(jl_poly))