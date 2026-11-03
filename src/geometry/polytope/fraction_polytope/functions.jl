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
    return zeros(Rational{BigInt}, Polyhedra.fulldim(poly))
  end
  return sum(vertices) .// numVertices
end

function get_vertices_outer(poly::Polyhedron)::Matrix{Float64}
  verts = collect(Polyhedra.points(Polyhedra.vrep(poly)))
  ambDim = Polyhedra.fulldim(poly)
  
  if isempty(verts)
    return Matrix{Float64}(undef, 0, ambDim)
  end

  corners_exact = Vector{Vector{Rational{BigInt}}}()
  
  # Generar las 2^n esquinas para la caja de redondeo de cada vértice
  for v in verts
    # Para cada coordenada, obtenemos los bordes exactos usando RoundDown y RoundUp
    bounds = [(Rational{BigInt}(Float64(v[j], RoundDown)), 
               Rational{BigInt}(Float64(v[j], RoundUp))) for j in 1:ambDim]
               
    # Hacemos el producto cartesiano para sacar todas las combinaciones posibles
    for corner in Iterators.product(bounds...)
        push!(corners_exact, collect(corner))
    end
  end

  # Calcular cápsula convexa exacta de todas las esquinas generadas
  poly_outer = polyhedron(Polyhedra.vrep(corners_exact), lib)
  Polyhedra.removevredundancy!(poly_outer)

  outer_verts = collect(Polyhedra.points(Polyhedra.vrep(poly_outer)))
  
  # Ahora es 100% seguro pasarlos a Float64 (son flotantes exactos por construcción)
  mat = Matrix{Float64}(undef, length(outer_verts), ambDim)
  for (i, p) in enumerate(outer_verts)
    for j in 1:ambDim
      mat[i, j] = Float64(p[j])
    end
  end
  return mat
end

function get_hrep_outer(poly::Polyhedron)::Tuple{Matrix{Float64}, Vector{Float64}}
  hs = collect(Polyhedra.halfspaces(Polyhedra.hrep(poly)))
  vertices = collect(Polyhedra.points(Polyhedra.vrep(poly))) 
  
  numHalfspaces = length(hs)
  ambDim = Polyhedra.fulldim(poly)
  
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

function get_hrep_inner(poly::Polyhedron)::Tuple{Matrix{Float64}, Vector{Float64}}
  hs = collect(Polyhedra.halfspaces(Polyhedra.hrep(poly)))
  verts = collect(Polyhedra.points(Polyhedra.vrep(poly))) 
  ambDim = Polyhedra.fulldim(poly)
  
  if isempty(hs)
    return Matrix{Float64}(undef, 0, ambDim), Vector{Float64}(undef, 0)
  end
  if isempty(verts)
    return get_hrep(poly) # Fallback si no está acotado
  end

  # 1. Calcular ξ_j (máximo valor absoluto por dimensión, redondeado hacia arriba)
  xi = zeros(Rational{BigInt}, ambDim)
  for j in 1:ambDim
     max_val = maximum(abs(v[j]) for v in verts)
     xi[j] = Rational{BigInt}(Float64(max_val, RoundUp))
  end

  num_rows = length(hs) + 2 * ambDim
  A_inner = Matrix{Float64}(undef, num_rows, ambDim)
  b_inner = Vector{Float64}(undef, num_rows)
  
  for (i, h) in enumerate(hs)
    a_exact = h.a
    beta_exact = h.β
    
    a_tilde = Float64.(a_exact)
    a_tilde_rat = Rational{BigInt}.(a_tilde)
    
    # 2. Suma de errores exacta en valor absoluto
    error_sum = sum(abs(a_exact[j] - a_tilde_rat[j]) * xi[j] for j in 1:ambDim)
    
    # 3. Compensación de la rotación en b
    b_exact = beta_exact - error_sum
    
    for j in 1:ambDim
      A_inner[i, j] = a_tilde[j]
    end
    b_inner[i] = Float64(b_exact, RoundDown)
  end
  
  # 4. Agregar las inecuaciones de la caja (±x_j <= ξ_j)
  row_idx = length(hs) + 1
  for j in 1:ambDim
    # +x_j <= ξ_j
    for k in 1:ambDim; A_inner[row_idx, k] = (k == j ? 1.0 : 0.0); end
    b_inner[row_idx] = Float64(xi[j], RoundDown)
    row_idx += 1
    
    # -x_j <= ξ_j
    for k in 1:ambDim; A_inner[row_idx, k] = (k == j ? -1.0 : 0.0); end
    b_inner[row_idx] = Float64(xi[j], RoundDown)
    row_idx += 1
  end
  
  return A_inner, b_inner
end

function get_hrep_normalized_outer(poly::Polyhedron)::Tuple{Matrix{Float64}, Vector{Float64}}
  hs = collect(Polyhedra.halfspaces(Polyhedra.hrep(poly)))
  vertices = collect(Polyhedra.points(Polyhedra.vrep(poly))) 
  
  numHalfspaces = length(hs)
  ambDim = Polyhedra.fulldim(poly)
  
  if numHalfspaces == 0
    return Matrix{Float64}(undef, 0, ambDim), Vector{Float64}(undef, 0)
  end
  
  A = Matrix{Float64}(undef, numHalfspaces, ambDim)
  b = Vector{Float64}(undef, numHalfspaces)
  
  for (i, h) in enumerate(hs)
    aInterval = Interval.(h.a)
    normsq = sum(aInterval .^ 2)
    normInv = 1.0 / sqrt(normsq) 
    aNormInterval = aInterval .* normInv
    
    for j in 1:ambDim
      A[i, j] = mid(aNormInterval[j])
    end
    
    if isempty(vertices)
      bInterval = Interval(h.β) * normInv 
      b[i] = sup(bInterval)
    else
      ratA = Rational{BigInt}.(A[i, :])
      maxExactb = maximum(sum(ratA[j] * v[j] for j in 1:ambDim) for v in vertices)
      b[i] = Float64(maxExactb, RoundUp) 
    end
  end
  
  return A, b
end

function get_boundaries(poly::Polyhedron)::Vector{Polyhedron}
  hs = collect(Polyhedra.halfspaces(Polyhedra.hrep(poly)))
  facets = Vector{Polyhedron}()
  for h in hs
    hp = Polyhedra.HyperPlane(h.a, h.β)
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

function get_halfspace_points_outer(poly::Polyhedron)::Vector{Matrix{Float64}}
  A, b = get_hrep_outer(poly)
  ambDim = Polyhedra.fulldim(poly)
  result = Vector{Matrix{Float64}}()
  
  if length(b) == 0
    return result
  end
  
  ratA = Rational{BigInt}.(A)
  ratb = Rational{BigInt}.(b)
  poly_outer = polyhedron(Polyhedra.hrep(ratA, ratb), lib)
  Polyhedra.removehredundancy!(poly_outer)
  verts = collect(Polyhedra.points(Polyhedra.vrep(poly_outer)))
  
  for i in 1:length(b)
    facePoints = filter(p -> ratA[i, :] ⋅ p == ratb[i], verts)
    
    # Si la cara intersecta suficientes vértices reales, los usamos
    if length(facePoints) >= ambDim
        mat = Matrix{Float64}(undef, ambDim, ambDim)
        for (k, p) in enumerate(facePoints[1:ambDim])
          for j in 1:ambDim
             mat[k, j] = Float64(p[j])
          end
        end
        push!(result, mat)
    else
        # FALLBACK EXACTO: Cara redundante (ej. Bounding Box).
        # Generamos los puntos algebraicamente usando fracciones puras.
        mat = Matrix{Float64}(undef, ambDim, ambDim)
        max_idx = argmax(abs.(ratA[i, :])) # Eje seguro para evitar división por 0
        
        # Primer punto base
        p1 = zeros(Rational{BigInt}, ambDim)
        p1[max_idx] = ratb[i] // ratA[i, max_idx]
        
        for j in 1:ambDim; mat[1, j] = Float64(p1[j]); end
        
        # Puntos directores restantes
        row = 2
        for j in 1:ambDim
            if j != max_idx
                pj = copy(p1)
                pj[max_idx] -= ratA[i, j]
                pj[j] += ratA[i, max_idx]
                for k in 1:ambDim; mat[row, k] = Float64(pj[k]); end
                row += 1
            end
        end
        push!(result, mat)
    end
  end
  
  return result
end

function get_halfspace_points_inner(poly::Polyhedron)::Vector{Matrix{Float64}}
  A, b = get_hrep_inner(poly)
  ambDim = Polyhedra.fulldim(poly)
  result = Vector{Matrix{Float64}}()
  
  if length(b) == 0
    return result
  end
  
  ratA = Rational{BigInt}.(A)
  ratb = Rational{BigInt}.(b)
  poly_inner = polyhedron(Polyhedra.hrep(ratA, ratb), lib)
  Polyhedra.removehredundancy!(poly_inner)
  verts = collect(Polyhedra.points(Polyhedra.vrep(poly_inner)))
  
  for i in 1:length(b)
    facePoints = filter(p -> ratA[i, :] ⋅ p == ratb[i], verts)
    
    if length(facePoints) >= ambDim
        mat = Matrix{Float64}(undef, ambDim, ambDim)
        for (k, p) in enumerate(facePoints[1:ambDim])
          for j in 1:ambDim
             mat[k, j] = Float64(p[j])
          end
        end
        push!(result, mat)
    else
        mat = Matrix{Float64}(undef, ambDim, ambDim)
        max_idx = argmax(abs.(ratA[i, :]))
        
        p1 = zeros(Rational{BigInt}, ambDim)
        p1[max_idx] = ratb[i] // ratA[i, max_idx]
        
        for j in 1:ambDim; mat[1, j] = Float64(p1[j]); end
        
        row = 2
        for j in 1:ambDim
            if j != max_idx
                pj = copy(p1)
                pj[max_idx] -= ratA[i, j]
                pj[j] += ratA[i, max_idx]
                for k in 1:ambDim; mat[row, k] = Float64(pj[k]); end
                row += 1
            end
        end
        push!(result, mat)
    end
  end
  
  return result
end