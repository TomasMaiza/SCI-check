using Test
using IntervalArithmetic
using IntervalMatrices
using LinearAlgebra

# 1. Importamos los archivos que vamos a testear
# Asegurate de que los nombres coincidan exactamente con tus archivos
include("../src/polytope_subregions/interval_imp/approximations/strategy.jl")
include("../src/polytope_subregions/interval_imp/matrices.jl")
include("../src/polytope_subregions/interval_imp/approximations/euler.jl")

@testset "Suite de Pruebas SCI-check" begin

    @testset "Pruebas de matrices_2.jl" begin
        
        @testset "sas_augmented_matrix" begin
            A = IntervalMatrix([1.0 2.0; 3.0 4.0])
            b = [interval(5.0), interval(6.0)]
            homA = sas_augmented_matrix(A, b)
            
            # Caso Normal: Dimensión debe ser (n+1) x (n+1) -> 3x3
            @test size(homA) == (3, 3)
            # Verificamos que la última fila sea [0, 0, 0] exactamente
            @test all(inf.(Matrix(homA)[3, :]) .== 0.0)
            @test all(sup.(Matrix(homA)[3, :]) .== 0.0)
            # Verificamos que 'b' se colocó en la última columna correctamente
            @test homA[1, 3] == interval(5.0)
        end

        @testset "polytope_augmented_matrix" begin
            H = IntervalMatrix([1.0 0.0; 0.0 1.0])
            c = [interval(2.0), interval(3.0)]
            homH = polytope_augmented_matrix(H, c)
            
            # Caso Normal: Dimensión debe ser n x (n+1) -> 2x3
            @test size(homH) == (2, 3)
            # El vector c entra con signo negativo
            @test homH[1, 3] == interval(-2.0)
            @test homH[2, 3] == interval(-3.0)
        end

        @testset "partition_matrices" begin
            H = IntervalMatrix([1.0 0.0; 0.0 1.0])
            c = [interval(1.0), interval(1.0)]
            A = IntervalMatrix([-1.0 0.0; 0.0 -1.0])
            b = [interval(0.0), interval(0.0)]
            
            # Caso Normal con h > 0
            Hplus, Hminus = partition_matrices(H, c, A, b, 0.1)
            # homH es 2x3, se apila consigo misma multiplicada -> 4x3
            @test size(Hplus) == (4, 3)
            @test size(Hminus) == (4, 3)
            
            # Caso Borde: h = 0.0
            # Si h=0, Hplus y Hminus deberían ser simplemente [homH; homH]
            Hp_zero, Hm_zero = partition_matrices(H, c, A, b, 0.0)
            @test Hp_zero[1:2, :] == Hp_zero[3:4, :]
            @test Hm_zero[1:2, :] == Hm_zero[3:4, :]
        end

        @testset "partition_matrices_bound" begin
            H = IntervalMatrix([1.0 0.0; 0.0 1.0])
            c = [interval(1.0), interval(1.0)]
            
            # Caso Normal
            bound = partition_matrices_bound(H, c, 0.5, 0.1)
            @test size(bound, 1) == 4
            @test bound[1] == interval(-0.5) # -r
            @test bound[3] == interval(-0.1) # -midErrorBound
            
            # Caso Borde: r = 0, midErrorBound = 0
            bound_zero = partition_matrices_bound(H, c, 0.0, 0.0)
            @test all(inf.(bound_zero) .== 0.0)
        end

        @testset "augmented_x" begin
            x = [interval(2.5), interval(-1.5)]
            hom_x = augmented_x(x)
            
            # Verificamos que agrega la dimensión y el 1.0 al final
            @test length(hom_x) == 3
            @test hom_x[3] == interval(1.0)
            @test hom_x[1] == interval(2.5)
        end
    end

    @testset "Pruebas de euler_3.jl" begin
        # Setup: Creamos un sistema dummy para inyectar en la estrategia de Euler
        A_dummy = IntervalMatrix([0.0 1.0; -1.0 0.0])
        b_dummy = [interval(0.0), interval(0.0)]
        homA_dummy = sas_augmented_matrix(A_dummy, b_dummy)
        S_dummy = [[interval(1.0), interval(1.0)], [interval(-1.0), interval(-1.0)]]
        
        # Instanciamos la estrategia
        euler_strat = Euler(A_dummy, b_dummy, homA_dummy, S_dummy)
        
        @testset "Constructor Euler" begin
            # Verificamos que el constructor externo (o interno) guardó bien los datos
            @test size(euler_strat.A) == (2, 2)
            @test length(euler_strat.S) == 2
        end

        @testset "apply" begin
            # Caso Normal: paso s = 0.1
            x = [1.0, 1.0] # Vector exacto Float64
            x_next = apply(euler_strat, 0.1, x)
            @test length(x_next) == 2
            @test typeof(x_next) == Vector{Interval{Float64}}
            
            # Caso Borde: paso s = 0.0 -> el estado no debería cambiar (x_next == x)
            x_zero = apply(euler_strat, 0.0, x)
            @test inf(x_zero[1]) == 1.0 && sup(x_zero[1]) == 1.0
        end

        @testset "_get_M" begin
            # Calculamos M manualmente. 
            # normA es 1.0. Para S = [1, 1], A*x+b = [1, -1], su norma 2 es sqrt(2)
            M_int = _get_M(euler_strat, interval(1.0))
            @test typeof(M_int) == Interval{Float64}
            # Comprobamos que contiene el valor aproximado de raíz de 2
            @test inf(M_int) <= sqrt(2.0) <= sup(M_int)
        end

        @testset "error_bound" begin
            # Caso Borde: sin error inicial y sin paso (tau = 0.0)
            err_zero = error_bound(euler_strat, interval(0.0), 0.0)
            @test inf(err_zero) == 0.0 && sup(err_zero) == 0.0
            
            # Caso Normal: r = 0, tau = 0.1
            err_normal = error_bound(euler_strat, interval(0.0), 0.1)
            # El error introducido por la aproximación debe ser estrictamente positivo
            @test inf(err_normal) >= 0.0 
        end

        @testset "error_sequence" begin
            # Caso Normal: K = 3
            seq = error_sequence(euler_strat, 0.1, 3)
            # Si K=3, la secuencia tiene K+1 (4) elementos
            @test length(seq) == 4
            # El primer elemento r0 debe ser 0.0
            @test seq[1] == interval(0.0)
            # El error debe ser creciente r_k <= r_{k+1}
            @test sup(seq[1]) <= inf(seq[2])
            @test sup(seq[2]) <= inf(seq[3])
        end

        @testset "get_matrix" begin
            # Caso Normal: s = 0.1
            phi = get_matrix(euler_strat, 0.1)
            @test size(phi) == (3, 3) # Dimensión de homA
            
            # Caso Borde: s = 0.0
            # Si el paso es 0, la matriz de aproximación Phi debe ser exactamente la Identidad
            phi_zero = get_matrix(euler_strat, 0.0)
            @test phi_zero[1, 1] == interval(1.0)
            @test phi_zero[1, 2] == interval(0.0)
        end
    end
end