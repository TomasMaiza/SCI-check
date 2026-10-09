using IntervalArithmetic
using IntervalMatrices
using LinearAlgebra

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

function partition_matrices(H::IntervalMatrix, c::Vector{Interval{Float64}}, 
                            A::IntervalMatrix, b::Vector{Interval{Float64}},
                            h::Float64)::(IntervalMatrix, IntervalMatrix)
  homA = sas_augmented_matrix(A, b)
  homH = polytope_augmented_matrix(H, c)
  dimA = size(homA, 1)
  I = Matrix{Interval{Float64}}(I, dimA, dimA)

  Hplus = [Matrix(homH);
           Matrix(homH * (I + h/2 * homA))]
  
  Hminus = [Matrix(homH);
            Matrix(homH * (I - h/2 * homA))]

  return IntervalMatrix(Hplus), IntervalMatrix(Hminus)
end

function partition_matrices_bound(H::IntervalMatrix, c::Vector{Interval{Float64}}, 
                                  r::Float64, 
                                  midErrorBound::Float64)::Vector{Interval{Float64}}
  homH = polytope_augmented_matrix(H, c)
  dim = size(homH, 1)
  ones = ones(Interval{Float64}, dim, 1)
  c = [-r * ones;
       -midErrorBound * ones]

  return c
end

function augmented_x(x::Vector{Interval{Float64}})::Vector{Interval{Float64}}
  return [x; interval(1.0)]
end