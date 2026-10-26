struct Hyperplane{T}
  points::Vector{Point{T}}

  function Hyperplane{T}(points::Vector{Point{T}}) where T
    if isempty(points)
      throw(ArgumentError("El hiperplano debe contener al menos un punto."))
    end
    new{T}(points)
  end
end

function get_points(h::Hyperplane{T})::Vector{Point{T}} where T
  return h.points
end