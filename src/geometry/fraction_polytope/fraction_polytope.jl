using Polyhedra
using CDDLib

const FractionPoint = Point{Rational{BigInt}}
const FractionEdge  = Edge{Rational{BigInt}}

struct FractionPolytope <: AbstractPolytope
  intDim::Int
  ambDim::Int
  boundaries::Vector{AbstractPolytope}
  vertices::Vector{FractionPoint}
  A::Matrix{Rational{BigInt}}
  b::Vector{Rational{BigInt}}
  supportingHyperplane::Union{Nothing, Hyperplane{Rational{BigInt}}}
  halfspaces::Vector{Halfspace{Rational{BigInt}}}
  centroid::FractionPoint
end

function FractionPolytope(;
                          intDim::Int,
                          ambDim::Int,
                          vertices::Union{Nothing, Vector{FractionPoint}} = nothing,
                          A::Union{Nothing, Matrix{Rational{BigInt}}} = nothing,
                          b::Union{Nothing, Vector{Rational{BigInt}}} = nothing)::FractionPolytope
  if (A === nothing || b === nothing) && vertices === nothing
    throw(ArgumentError("Inicialización inválida: Proveer vértices o (A, b)"))
  end
end