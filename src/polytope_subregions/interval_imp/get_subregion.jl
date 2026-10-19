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
  errorSeq = error_sequence(approx, h, K)
  phi = get_matrix(approx, h)

  dim = size(phi, 1)
  phi_k = IntervalMatrix(Matrix{Interval{Float64}}(I, dim, dim))

  Hplus, Hminus = partition_matrices(H, c, A, b, h)
  subregionH = Vector{Matrix{Interval{Float64}}}()
  subregionc = Vector{Vector{Interval{Float64}}}()

  for k in 0:K
    r = errorSeq[k + 1]
    midr = error_bound(approx, r, h / 2.0)
    cBound = partition_matrices_bound(H, c, sup(r), sup(midr))

    if k > 0
      push!(subregionH, Matrix(Hminus * phi_k))
      push!(subregionc, cBound)    
    end

    if k < K
      push!(subregionH, Matrix(Hplus * phi_k))
      push!(subregionc, cBound)
    end

    phi_k = phi * phi_k
  end

  matrixH = reduce(vcat, subregionH)
  matrixc = reduce(vcat, subregionc)

  matrixA = matrixH[:, 1:dim-1]
  matrixb_col = matrixH[:, dim]
  matrixb = matrixc .- matrixb_col

  return IntervalMatrix(matrixA), matrixb
end