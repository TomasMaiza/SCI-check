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

  lib = CDDLib.Library(:exact) # solver en modo exacto (GMP) para evitar punto flotante
  local finalVertices::Vector{FractionPoint}
  local finalA::Matrix{Rational{BigInt}}
  local finalb::Vector{Rational{BigInt}}

  if vertices === nothing # en este caso se inicializó el politopo con H-rep
    h = Polyhedra.hrep(A, b)
    poly = polyhedron(h, lib)
    Polyhedra.removehredundancy!(poly)
    finalVertices = collect(Polyhedra.points(Polyhedra.vrep(poly)))
    hs = Polyhedra.halfspaces(Polyhedra.hrep(poly))
    finalA = isempty(hs) ? Matrix{Rational{BigInt}}(undef, 0, ambDim) : mapreduce(x -> transpose(x.a), vcat, hs)
    finalb = [x.β for x in hs] # a*x <= β
  else # en este caso se inicializó con vértices
    v = Polyhedra.vrep(vertices)
    poly = polyhedron(v, lib)
    Polyhedra.removehredundancy!(poly)
    hs = Polyhedra.halfspaces(Polyhedra.hrep(poly))
    finalA = isempty(hs) ? Matrix{Rational{BigInt}}(undef, 0, ambDim) : mapreduce(x -> transpose(x.a), vcat, hs)
    finalb = [x.β for x in hs]
    finalVertices = vertices
  end

  finalCentroid = isempty(final_vertices) ? zeros(Rational{BigInt}, ambDim) : sum(finalVertices) .// length(finalVertices)
  return FractionPolytope(intDim, ambDim, AbstractPolytope[], finalVertices, finalA, finalb, nothing, Halfspace[], finalCentroid)
end