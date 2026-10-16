using IntervalArithmetic
using IntervalMatrices
using LinearAlgebra
using matrices

struct Taylor <: ApproximationStrategy
  A::IntervalMatrix
  b::Vector{Interval{Float64}}
  homA::IntervalMatrix
  S::Vector{Vector{Interval{Float64}}}
  scaling::Int
  order::Int
  polyRad::Interval{Float64}
end

function Taylor(A::IntervalMatrix,
                b::Vector{Interval{Float64}},
                homA::IntervalMatrix,
                S::Vector{Vector{Interval{Float64}}},
                scaling::Int,
                order::Int)
  R_S_max = -1.0
  for x in S
    homx = augmented_x(x)
    val = norm(mag.(homx), 2) # extraemos la magnitud absoluta para calcular la norma en Float64
    if val > R_S_max
      R_S_max = val
    end
  end
  polyRad = interval(R_S_max)

  return Taylor(A, b, homA, S, scaling, order, polyRad)
end

function apply(approx::Taylor, h::Float64, x::Vector{Float64})::Vector{Interval{Float64}}
  homx = augmented_x(interval.(x))
  Phi = get_matrix(approx, h)
  res = Phi * homx
  return res[1:size(approx.A, 1)]
end

function error_bound(approx::Taylor, r::Interval{Float64}, tau::Float64)::Interval{Float64}

end

function error_sequence(approx::Taylor, h::Float64, K::Int)::Vector{Interval{Float64}}

end

function get_matrix(approx::Taylor, s::Float64)::IntervalMatrix

end