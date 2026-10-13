using IntervalArithmetic
using IntervalMatrices
using LinearAlgebra

struct Euler <: ApproximationStrategy
  A::IntervalMatrix
  b::Vector{Interval{Float64}}
  homA::IntervalMatrix
  S::Vector{Vector{Interval{Float64}}}
end

function Euler(A::IntervalMatrix, 
               b::Vector{Interval{Float64}}, 
               homA::IntervalMatrix, 
               S::Vector{Vector{Interval{Float64}}})::Euler
    return Euler(A, b, homA, S)
end

function apply(approx::Euler, s::Float64, x::Vector{Float64})::Vector{Interval{Float64}}
  return x + s * (approx.A * x + approx.b)
end

function error_bound(approx::Euler, 
                     r::Float64, 
                     tau::Float64)::Vector{Interval{Float64}}
  normA = opnorm(approx.A, 2)
  M = _get_M(approx, normA)
  return r * (1.0 + normA * tau) + M * (exp(normA * tau) - 1.0 - normA * tau)
end

function _get_M(approx::Euler, normA::Float64)::Float64
  m = -1.0
  for x in approx.S
    norm = norm(approx.A * x + approx.b, 2)
    supVal = sup(norm)
    if supVal < m
      m = supVal
  end
  return (1.0 / normA) * m
end

function error_sequence(approx::Euler, h::Float64, K::Int)::Vector{Interval{Float64}}
  
end

function get_matrix(approx::Euler, s::Float64)::IntervalMatrix
  dim = size(approx.homA, 1)
  I = IntervalMatrix(Matrix{Interval{Float64}}(I, dim, dim))
  return I + s * approx.homA
end