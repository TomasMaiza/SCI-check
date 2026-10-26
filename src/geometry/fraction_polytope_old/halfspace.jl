struct Halfspace{T}
  points::Union{Nothing, Vector{Point{T}}}
  normal::Union{Nothing, Vector{T}}
  b::Union{Nothing, T}

  function Halfspace{T}(;
                        points::Union{Nothing, Vector{Point{T}}} = nothing, 
                        normal::Union{Nothing, Vector{T}} = nothing, 
                        b::Union{Nothing, T} = nothing) where T
    if points === nothing && (normal === nothing || b === nothing)
      throw(ArgumentError("Inicialización inválida: Proveer puntos o (normal, b)."))
    end
    new{T}(points, normal, b)
  end
end

function get_points(h::Halfspace{T})::Vector{Point{T}} where T
  if h.points === nothing
    error("Los puntos no fueron definidos en este semiespacio.")
  end
  return h.points
end

function get_normal(h::Halfspace{T})::Vector{T} where T
  if h.normal === nothing
    error("Falta el vector normal.")
  end
  return h.normal
end