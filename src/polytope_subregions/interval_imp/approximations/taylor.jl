using IntervalArithmetic
using IntervalMatrices
using LinearAlgebra

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
end

function apply(approx::Taylor, s::Float64, x::Vector{Float64})::Vector{Interval{Float64}}

end

function error_bound(approx::Taylor, r::Interval{Float64}, tau::Float64)::Interval{Float64}

end

function error_sequence(approx::Taylor, h::Float64, K::Int)::Vector{Interval{Float64}}

end

function get_matrix(approx::Taylor, s::Float64)::IntervalMatrix

end