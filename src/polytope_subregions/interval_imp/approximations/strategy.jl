using IntervalArithmetic
using IntervalMatrices
using LinearAlgebra

abstract type ApproximationStrategy end

function apply(approx::ApproximationStrategy, s::Float64, x::Vector{Float64})::Vector{Interval{Float64}}
  error("El método apply() no está implementado para la estrategia $(typeof(approx))")
end

function error_bound(approx::ApproximationStrategy, r::Interval{Float64}, tau::Float64)::Interval{Float64}
  error("El método error_bound() no está implementado para la estrategia $(typeof(approx))")
end

function error_sequence(approx::ApproximationStrategy, h::Float64, K::Int)::Vector{Interval{Float64}}
  error("El método error_sequence() no está implementado para la estrategia $(typeof(approx))")
end

function get_matrix(approx::ApproximationStrategy, s::Float64)::IntervalMatrix
  error("El método get_matrix() no está implementado para la estrategia $(typeof(approx))")
end