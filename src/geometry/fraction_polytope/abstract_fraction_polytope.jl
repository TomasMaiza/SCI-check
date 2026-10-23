# Politopos con fracciones utilizando el patrón Strategy/Composite

const Point{T} = Vector{T}
const Edge{T} = Tuple{Point{T}, Point{T}}
abstract type Halfspace{T} end
abstract type Hyperplane{T} end

# Clase base abstracta para representar politopos.
abstract type AbstractPolytope{T} end

function get_vertices(p::AbstractPolytope{T})::Vector{Point{T}} where T
  # Permite obtener los vértices del politopo.
  error("El método get_vertices() no está implementado para el tipo $(typeof(p))")
end

function get_hrep(p::AbstractPolytope{T})::Tuple{Matrix{T}, Vector{T}} where T
  # Permite obtener las matrices A y b que definen al politopo (Ax <= b).
  error("El método get_hrep() no está implementado para el tipo $(typeof(p))")
end

function get_hrep_normalized(p::AbstractPolytope{T})::Tuple{Matrix{T}, Vector{T}} where T
  # Permite obtener las matrices A y b que definen al politopo (Ax <= b) normalizadas.
  error("El método get_hrep_normalized() no está implementado para el tipo $(typeof(p))")
end

function get_edges(p::AbstractPolytope{T})::Vector{Edge{T}} where T
  # Retorna las aristas del politopo.
  error("El método get_edges() no está implementado para el tipo $(typeof(p))")
end

function get_boundaries(p::AbstractPolytope{T})::Vector{AbstractPolytope{T}} where T
  # Devuelve las caras del politopo como objetos AbstractPolytope (Patrón Composite).
  error("El método get_boundaries() no está implementado para el tipo $(typeof(p))")
end

function get_halfspaces(p::AbstractPolytope{T})::Vector{Halfspace{T}} where T
  # Devuelve la lista de los semiespacios que definen al politopo.
  error("El método get_halfspaces() no está implementado para el tipo $(typeof(p))")
end

function get_supporting_hyperplane(p::AbstractPolytope{T})::Hyperplane{T} where T
  # Retorna el hiperplano que contiene al politopo si intDim < ambDim.
  error("El método get_supporting_hyperplane() no está implementado para el tipo $(typeof(p))")
end

function get_centroid(p::AbstractPolytope{T})::Point{T} where T
  # Retorna el centroide del politopo.
  error("El método get_centroid() no está implementado para el tipo $(typeof(p))")
end

"""
"""
function reduce!(p::AbstractPolytope{T}) where T
  # Elimina las inecuaciones redundantes.
  # En Julia los métodos que modifican el estado interno del objeto llevan un ! al final
    error("El método reduce!() no está implementado para el tipo $(typeof(p))")
end