using IntervalArithmetic
using IntervalMatrices
using LinearAlgebra

function get_subregion(approx::ApproximationStrategy,
                       H::IntervalMatrix,
                       c::Vector{Interval{Float64}},
                       A::IntervalMatrix,
                       b::Vector{Interval{Float64}},
                       h::Float64,
                       K::Int)::Tuple{IntervalMatrix, Vector{Interval{Float64}}}
  
end