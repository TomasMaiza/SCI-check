using IntervalArithmetic
using IntervalMatrices

function sas_augmented_matrix(A::IntervalMatrix, b::Vector{Interval{Float64}})::IntervalMatrix
  n = size(A, 1) # obtiene el número de filas
  zerosRow = zeros(Interval{Float64}, 1, n) # fila de intervalos [0, 0]
  homA = [Matrix(A)  b; 
          zerosRow   interval(0.0)]
  return IntervalMatrix(homA)
end

function polytope_augmented_matrix(H::IntervalMatrix, c::Vector{Interval{Float64}})::IntervalMatrix
  homH = [Matrix(H) -c]
  return IntervalMatrix(homH)
end

