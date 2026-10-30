using Polyhedra
using CDDLib
using IntervalArithmetic

const Interval = IntervalArithmetic.Interval

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

function get_centroid(poly::Polyhedron)::Vector{Rational{BigInt}}
  vertices = collect(Polyhedra.points(Polyhedra.vrep(poly)))
  numVertices = length(vertices)
  if numVertices == 0
    return zeros(Rational{BigInt}, Polyhedra.ambientdim(poly))
  end
  return sum(vertices) .// numVertices
end

function get_vertices(poly::Polyhedron)::Matrix{Float64}
  vertices = collect(Polyhedra.points(Polyhedra.vrep(poly)))
  numVertices = length(vertices)
  ambDim = Polyhedra.ambientdim(poly)

  if numVertices == 0
    return Matrix{Float64}(undef, 0, Polyhedra.ambientdim(poly))
  end

  verticesMatrix = Matrix{Float64}(undef, numVertices, Polyhedra.ambientdim(poly))
  centroid = get_centroid(poly)

  for (i, p) in enumerate(vertices)
    for j in 1:ambDim
    verticesMatrix[i, j] = p[j] >= centroid[j] ? Float64(p[j], RoundUp) : Float64(p[j], RoundDown)
    end
  end
  return verticesMatrix
end

function get_hrep(poly::Polyhedron)::Tuple{Matrix{Float64}, Vector{Float64}}
  hs = collect(Polyhedra.halfspaces(Polyhedra.hrep(poly)))
  vertices = collect(Polyhedra.points(Polyhedra.vrep(poly))) 
  
  numHalfspaces = length(hs)
  ambDim = Polyhedra.ambientdim(poly)
  
  if numHalfspaces == 0
    return Matrix{Float64}(undef, 0, ambDim), Vector{Float64}(undef, 0)
  end
  
  A = Matrix{Float64}(undef, numHalfspaces, ambDim)
  b = Vector{Float64}(undef, numHalfspaces)
  
  for (i, h) in enumerate(hs)
    for j in 1:ambDim
      A[i, j] = Float64(h.a[j]) 
    end
    
    if isempty(vertices)
      b[i] = Float64(h.β, RoundUp) # caso borde: poliedro no acotado
    else
      ratA = Rational{BigInt}.(A[i, :]) # volvemos a fracciones para operar
      # Producto escalar exacto de la nueva normal con todos los vértices, buscamos el máximo
      maxExactb = maximum(sum(ratA[j] * v[j] for j in 1:ambDim) for v in vertices)
      b[i] = Float64(maxExactb, RoundUp) # redondeamos el máximo absoluto hacia arriba
    end
  end
  
  return A, b
end

function get_hrep_normalized(poly::Polyhedron)::Tuple{Matrix{Float64}, Vector{Float64}}
  hs = collect(Polyhedra.halfspaces(Polyhedra.hrep(poly)))
  vertices = collect(Polyhedra.points(Polyhedra.vrep(poly))) 
  
  numHalfspaces = length(hs)
  ambDim = Polyhedra.ambientdim(poly)
  
  if numHalfspaces == 0
    return Matrix{Float64}(undef, 0, ambDim), Vector{Float64}(undef, 0)
  end
  
  A = Matrix{Float64}(undef, numHalfspaces, ambDim)
  b = Vector{Float64}(undef, numHalfspaces)
  
  for (i, h) in enumerate(hs)
    aInterval = Interval.(h.a) # cálculo de la norma con intervalos
    normsq = sum(aInterval .^ 2)
    normInv = 1.0 / sqrt(normsq) 
    aNormInterval = aInterval .* normInv
    
    for j in 1:ambDim
      A[i, j] = mid(aNormInterval[j])
    end
    
    if isempty(vertices)
      bInterval = Interval(h.β) * normInv # caso borde: si no hay vértices, acotamos con el intervalo
      b[i] = inf(bInterval) # queremos achicar?
    else
      ratA = Rational{BigInt}.(A[i, :])
      maxExactb = maximum(sum(ratA[j] * v[j] for j in 1:ambDim) for v in vertices)
      b[i] = Float64(maxExactb, RoundDown) # queremos achicar?
    end
  end
  
  return A, b
end

function get_boundaries(poly::Polyhedron)::Vector{Polyhedron}
  hs = collect(Polyhedra.halfspaces(Polyhedra.hrep(poly)))
  facets = Vector{Polyhedron}()
  for h in hs
    hp = Polyhedra.Hyperplane(h.a, h.β)
    facet_hrep = intersect(Polyhedra.hrep(poly), hp)
    facet_poly = polyhedron(facet_hrep, lib)
    Polyhedra.removehredundancy!(facet_poly)
    push!(facets, facet_poly)
  end
  return facets
end

function get_edges(poly::Polyhedron)::Vector{Tuple{Vector{Float64}, Vector{Float64}}}
  hs = collect(Polyhedra.halfspaces(Polyhedra.hrep(poly)))
  hyps = collect(Polyhedra.hyperplanes(Polyhedra.hrep(poly)))
  verts = collect(Polyhedra.points(Polyhedra.vrep(poly)))
  
  constraints = vcat(hs, hyps) # unimos inecuaciones e igualdades
  edges = Vector{Tuple{Vector{Float64}, Vector{Float64}}}()
  numVerts = length(verts)
  
  for i in 1:numVerts
    for j in (i+1):numVerts
      v1 = verts[i]
      v2 = verts[j]
      
      # Buscamos qué restricciones comparten de forma estricta
      sharedConstraints = filter(c -> c.a ⋅ v1 == c.β && c.a ⋅ v2 == c.β, constraints)
      
      # Contamos cuántos vértices en TOTAL cumplen con estas restricciones compartidas
      count = sum(1 for v in verts if all(c -> c.a ⋅ v == c.β, sharedConstraints))
      
      # Si solo son v1 y v2, es matemáticamente una arista
      if count == 2
        push!(edges, (Float64.(v1), Float64.(v2)))
      end
    end
  end
  
  return edges
end

function get_halfspace_points(poly::Polyhedron)::Vector{Matrix{Float64}}
  hs = collect(Polyhedra.halfspaces(Polyhedra.hrep(poly)))
  vertices = collect(Polyhedra.points(Polyhedra.vrep(poly)))
  ambDim = Polyhedra.ambientdim(poly)
  
  result = Vector{Matrix{Float64}}()
  
  centroid = get_centroid(poly)
  
  for h in hs
    facePoints = filter(p -> h.a ⋅ p == h.β, vertices) # filtramos los vértices exactos que pertenecen a esta pared 
    
    mat = Matrix{Float64}(undef, length(facePoints), ambDim)
    for (i, p) in enumerate(facePoints)
      for j in 1:ambDim
         mat[i, j] = p[j] >= centroid[j] ? Float64(p[j], RoundUp) : Float64(p[j], RoundDown)
      end
    end
    push!(result, mat)
  end
  
  return result
end