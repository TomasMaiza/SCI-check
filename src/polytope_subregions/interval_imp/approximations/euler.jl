using IntervalArithmetic
using IntervalMatrices
using LinearAlgebra

struct Euler <: ApproximationStrategy
  A::IntervalMatrix
  b::Vector{Interval{Float64}}
  homA::IntervalMatrix
  S::Vector{Vector{Interval{Float64}}}
end

# si queda así borrarlo, Julia lo asume así por defecto
#function Euler(A::IntervalMatrix, 
#               b::Vector{Interval{Float64}}, 
#               homA::IntervalMatrix, 
#               S::Vector{Vector{Interval{Float64}}})::Euler
#    return Euler(A, b, homA, S)
#end

function apply(approx::Euler, s::Float64, x::Vector{Float64})::Vector{Interval{Float64}}
  return x + s * (approx.A * x + approx.b)
end

function error_bound(approx::Euler, 
                     r::Interval{Float64}, 
                     tau::Float64)::Interval{Float64}
  magA = mag.(Matrix(approx.A)) # matriz de magnitudes Float64 (valor absoluto máximo)
  normA = interval(opnorm(magA, 2))
  M = _get_M(approx, normA)
  oneInt = interval(1.0)
  return r * (oneInt + normA * tau) + M * (exp(normA * tau) - oneInt - normA * tau)
end

function _get_M(approx::Euler, normA::Interval{Float64})::Interval{Float64}
  m = -1.0
  for x in approx.S
    normVal = norm(approx.A * x + approx.b, 2)
    supVal = sup(normVal)
    if supVal > m
      m = supVal
    end
  end
  return (1.0 / normA) * m
end

function error_sequence(approx::Euler, h::Float64, K::Int)::Vector{Interval{Float64}}
  errorSeq = zeros(Interval{Float64}, K + 1)
  r = interval(0.0)
  for k in 1:K
    errorSeq[k] = r
    r = error_bound(approx, r, abs(h))
  end
  errorSeq[K + 1] = r
  return errorSeq
end

function get_matrix(approx::Euler, s::Float64)::IntervalMatrix
  dim = size(approx.homA, 1)
  matrixI = IntervalMatrix(Matrix{Interval{Float64}}(I, dim, dim))
  return matrixI + s * approx.homA
end