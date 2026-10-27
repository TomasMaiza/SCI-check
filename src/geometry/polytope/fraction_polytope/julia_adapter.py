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
  # retorna referencia al objeto Polyhedron de Julia
  return jl.create_polytope(vertices, A, b)

def get_poly_vertices(jlPoly) -> np.ndarray:
  # retorna una arreglo con los vértices del politopo
  return np.array(jl.get_vertices(jlPoly))

def get_poly_centroid(jlPoly) -> np.ndarray:
  # consulta el centroide del politopo
  return np.array(jl.get_centroid(jlPoly), dtype=np.float64)

def get_poly_hrep(jl_poly: Any) -> tuple[np.ndarray, np.ndarray]:
  # retorna las hrep del politopo Ax <= b
  A, b = jl.get_hrep(jl_poly)
  return np.array(A), np.array(b).flatten()

def get_poly_hrep_normalized(jl_poly: Any) -> tuple[np.ndarray, np.ndarray]:
  # retorna las hrep del politopo Ax <= b
  A, b = jl.get_hrep_normalized(jl_poly)
  return np.array(A), np.array(b).flatten()

def get_exact_facets(jl_poly: Any) -> list[Any]:
  # Devuelve una lista de referencias a sub-poliedros de Julia
  return list(jl.get_exact_facets(jl_poly))