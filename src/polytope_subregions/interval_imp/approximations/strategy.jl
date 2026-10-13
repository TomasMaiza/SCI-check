using IntervalArithmetic
using IntervalMatrices
using LinearAlgebra

abstract type ApproximationStrategy end

function apply(strategy::ApproximationStrategy, s::Float64, x::Vector{Float64})::Vector{Float64}
  error("El método apply() no está implementado para la estrategia $(typeof(strategy))")
end

function error_bound(strategy::ApproximationStrategy, r::Float64, tau::Float64)::Float64
  error("El método error_bound() no está implementado para la estrategia $(typeof(strategy))")
end

function error_sequence(strategy::ApproximationStrategy, h::Float64, K::Int)::Vector{Float64}
  error("El método error_sequence() no está implementado para la estrategia $(typeof(strategy))")
end

function get_matrix(strategy::ApproximationStrategy, s::Float64)::IntervalMatrix
  error("El método get_matrix() no está implementado para la estrategia $(typeof(strategy))")
end