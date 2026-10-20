using Test
using IntervalArithmetic
using IntervalMatrices
using LinearAlgebra

# 1. Importamos los archivos que vamos a testear
include("../src/polytope_subregions/interval_imp/approximations/strategy.jl")
include("../src/polytope_subregions/interval_imp/matrices.jl")
include("../src/polytope_subregions/interval_imp/approximations/euler.jl")
include("../src/polytope_subregions/interval_imp/approximations/taylor.jl")

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

    @testset "Pruebas de euler.jl" begin
        A_dummy = IntervalMatrix([0.0 1.0; -1.0 0.0])
        b_dummy = [interval(0.0), interval(0.0)]
        homA_dummy = sas_augmented_matrix(A_dummy, b_dummy)
        S_dummy = [[interval(1.0), interval(1.0)], [interval(-1.0), interval(-1.0)]]
        
        euler_strat = Euler(A_dummy, b_dummy, homA_dummy, S_dummy)
        
        @testset "Constructor Euler" begin
            @test size(euler_strat.A) == (2, 2)
            @test length(euler_strat.S) == 2
        end

        @testset "apply" begin
            x = [1.0, 1.0]
            x_next = apply(euler_strat, 0.1, x)
            @test length(x_next) == 2
            @test typeof(x_next) == Vector{Interval{Float64}}
            
            x_zero = apply(euler_strat, 0.0, x)
            @test inf(x_zero[1]) == 1.0 && sup(x_zero[1]) == 1.0
        end

        @testset "_get_M" begin
            M_int = _get_M(euler_strat, interval(1.0))
            @test typeof(M_int) == Interval{Float64}
            @test inf(M_int) <= sqrt(2.0) <= sup(M_int)
        end

        @testset "error_bound" begin
            err_zero = error_bound(euler_strat, interval(0.0), 0.0)
            @test inf(err_zero) == 0.0 && sup(err_zero) == 0.0
            
            err_normal = error_bound(euler_strat, interval(0.0), 0.1)
            @test inf(err_normal) >= 0.0 
        end

        @testset "error_sequence" begin
            seq = error_sequence(euler_strat, 0.1, 3)
            @test length(seq) == 4
            @test seq[1] == interval(0.0)
            @test sup(seq[1]) <= inf(seq[2])
            @test sup(seq[2]) <= inf(seq[3])
        end

        @testset "get_matrix" begin
            phi = get_matrix(euler_strat, 0.1)
            @test size(phi) == (3, 3) 
            
            phi_zero = get_matrix(euler_strat, 0.0)
            @test phi_zero[1, 1] == interval(1.0)
            @test phi_zero[1, 2] == interval(0.0)
        end
    end

    @testset "Pruebas de taylor.jl" begin
        # Setup similar a Euler pero agregamos scaling y order
        A_dummy = IntervalMatrix([0.0 1.0; -1.0 0.0])
        b_dummy = [interval(0.0), interval(0.0)]
        homA_dummy = sas_augmented_matrix(A_dummy, b_dummy)
        S_dummy = [[interval(1.0), interval(1.0)], [interval(-1.0), interval(-1.0)]]
        scaling = 2
        order = 3
        
        taylor_strat = Taylor(A_dummy, b_dummy, homA_dummy, S_dummy, scaling, order)

        @testset "Constructor Taylor" begin
            @test taylor_strat.scaling == 2
            @test taylor_strat.order == 3
            
            # Prueba del cálculo de R_S (polyRad):
            # Los vértices son [1, 1] y [-1, -1]. Aumentados son [1, 1, 1] y [-1, -1, 1].
            # La norma 2 de [1, 1, 1] es sqrt(1^2 + 1^2 + 1^2) = sqrt(3)
            @test inf(taylor_strat.polyRad) <= sqrt(3.0) <= sup(taylor_strat.polyRad)
        end

        @testset "apply" begin
            x = [1.0, 1.0] 
            x_next = apply(taylor_strat, 0.1, x)
            # Verificamos que se descartó la coordenada homogénea al final (dimensión 2, no 3)
            @test length(x_next) == 2
            @test typeof(x_next) == Vector{Interval{Float64}}
        end

        @testset "_get_M" begin
            M_int = _get_M(taylor_strat, interval(1.0))
            @test typeof(M_int) == Interval{Float64}
            @test inf(M_int) <= sqrt(2.0) <= sup(M_int)
        end
        
        @testset "_get_C_err" begin
            # Evaluamos la función específica de Taylor
            C_err = _get_C_err(taylor_strat, interval(1.0), 0.1)
            @test typeof(C_err) == Interval{Float64}
            @test inf(C_err) > 0.0
        end

        @testset "error_bound" begin
            err_zero = error_bound(taylor_strat, interval(0.0), 0.0)
            @test inf(err_zero) == 0.0 && sup(err_zero) == 0.0
            
            err_normal = error_bound(taylor_strat, interval(0.0), 0.1)
            @test inf(err_normal) >= 0.0 
        end

        @testset "error_sequence" begin
            seq = error_sequence(taylor_strat, 0.1, 3)
            @test length(seq) == 4
            @test seq[1] == interval(0.0)
            # El error en Taylor también debe ser monotónico creciente
            @test sup(seq[1]) <= inf(seq[2])
            @test sup(seq[2]) <= inf(seq[3])
        end

        @testset "get_matrix" begin
            phi = get_matrix(taylor_strat, 0.1)
            @test size(phi) == (3, 3) 
            
            # Si el paso es 0, Q es I, tau es 0, por ende Q^s debe ser la Identidad
            phi_zero = get_matrix(taylor_strat, 0.0)
            @test phi_zero[1, 1] == interval(1.0)
            @test phi_zero[1, 2] == interval(0.0)
        end
    end
end