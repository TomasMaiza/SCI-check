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

  matrixA     = matrixH[:, 1:dim-1]
  matrixb_col = matrixH[:, dim]
  matrixb     = matrixc .- matrixb_col

  ## Conversión de intervalos a Float64 con garantía
  # 1. Representante en Float64 de cada coeficiente: Ã
  Amid = mid.(matrixA)

  # 2. Matriz de radios R, respecto del double Ã (no del punto medio exacto).
  # mag da una cota SUPERIOR de |a_ij - Ã_ij|. Todas las entradas son >= 0.
  A_rad = mag.(matrixA .- Amid)

  # 3. Cota superior de |x_j| sobre P: ξ_j = max_v mag(v_j)  (máximo en un vértice)
  n_dim = size(matrixA, 2)
  x_max = [maximum(mag(v[j]) for v in approx.S) for j in 1:n_dim]

  # 4. Peor caso R·ξ, calculado en INTERVALOS (redondeo hacia afuera)
  slack = interval.(A_rad) * interval.(x_max)

  # 5. b̃ = inf(β - R·ξ), redondeado hacia abajo
  matrixb_safe = inf.(matrixb .- slack)
  ##

  return IntervalMatrix(interval.(Amid)), interval.(matrixb_safe)
end