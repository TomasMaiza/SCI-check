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
  magA = mag.(Matrix(approx.A)) # matriz de magnitudes Float64 (valor absoluto máximo)
  normA = interval(opnorm(magA, 2))
  M = _get_M(approx, normA)
  oneInt = interval(1.0)
  return r * (oneInt + normA * tau) + M * (exp(normA * tau) - oneInt - normA * tau)
end

function _get_M(approx::Taylor, normA::Interval{Float64})::Interval{Float64}
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

function error_sequence(approx::Taylor, h::Float64, K::Int)::Vector{Interval{Float64}}
  magHomA = mag.(Matrix(approx.homA))
  normHomA = interval(opnorm(magHomA, 2))
  Cerr = _get_C_err(approx, normHomA, h)
  errorSeq = zeros(Interval{Float64}, K + 1)
  for k in 0:K
    r = k * Cerr * exp(normHomA * h * k)
    errorSeq[k + 1] = r
  end
  return errorSeq
end

function _get_C_err(approx::Taylor, normHomA::Interval{Float64}, h::Float64)::Interval{Float64}
  num = (h * normHomA)^(approx.order + 1) * approx.polyRad
  den = (approx.scaling^approx.order) * interval(factorial(approx.order + 1))
  return interval(num / den)
end

function get_matrix(approx::Taylor, h::Float64)::IntervalMatrix
  tau = h / approx.scaling
  dim = size(approx.homA, 1)
  matrixI = IntervalMatrix(Matrix{Interval{Float64}}(I, dim, dim))
  Q = matrixI
  term = matrixI

  for j in 1:approx.order
    term = (term * (approx.homA * tau)) * interval(1.0 / j)
    Q = Q + term
  end
  
  return Q^approx.scaling
end