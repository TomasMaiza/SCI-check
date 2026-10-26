using Polyhedra
using CDDLib
using IntervalArithmetic

const FractionPoint = Vector{Rational{BigInt}}
const FractionEdge  = Tuple{FractionPoint, FractionPoint}
const lib = CDDLib.Library(:exact)

function create_polytope(vertices::Union{Nothing, Matrix{Float64}} = nothing,
                         A::Union{Nothing, Matrix{Float64}} = nothing,
                         b::Union{Nothing, Vector{Float64}} = nothing)::Polyhedron
  if (A === nothing || b === nothing) && vertices === nothing
    throw(ArgumentError("Inicialización inválida: Proveer vértices o (A, b)"))
  end

  local poly::Polyhedron

  if vertices === nothing # en este caso se inicializó el politopo con H-rep
    fractionA = Rational{BigInt}.(A)
    fractionb = Rational{BigInt}.(b)
    h = Polyhedra.hrep(fractionA, fractionb)
    poly = polyhedron(h, lib)
  else # en este caso se inicializó con vértices
    fractionVert = [Rational{BigInt}.(row) for row in eachrow(vertices)]
    v = Polyhedra.vrep(fractionVert)
    poly = polyhedron(v, lib)
  end
  Polyhedra.removehredundancy!(poly)
  return poly
end

function get_vertices(poly::Polyhedron)::Matrix{Float64}
  vertices = collect(Polyhedra.points(Polyhedra.vrep(poly)))
  numVertices = length(vertices)

  if numVertices == 0
    return Matrix{Float64}(undef, 0, Polyhedra.ambientdim(poly))
  end

  verticesMatrix = Matrix{Float64}(undef, numVertices, Polyhedra.ambientdim(poly))
  for (i, p) in enumerate(vertices)
    verticesMatrix[i, :] = Float64.(p)
  end
  return verticesMatrix
end