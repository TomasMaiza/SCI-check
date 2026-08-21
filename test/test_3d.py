import numpy as np
from coverage_checker import CoverageChecker3D, PredicatesFactory
from geometry import GeometryFactory, Geometry3d
from common import PolytopeMap, VerticesIndex, EdgesIndex, OrientResult, setup_logger

def create_mock_3d_box(geom, xmin, xmax, ymin, ymax, zmin, zmax) -> list:
    """
    Crea una lista de 6 Halfspace3D que representan una caja.
    Los puntos están ordenados en sentido ANTIHORARIO vistos desde afuera,
    garantizando que el vector normal apunte hacia el exterior del volumen.
    """
    def p(x, y, z): return geom.create_point((x, y, z))
    
    # 1. BOTTOM (Plano Z = zmin). Normal apunta hacia -Z.
    # Mirando desde abajo, antihorario es Y+, luego X+
    f_bottom = geom.create_halfspace((p(xmin, ymin, zmin), p(xmin, ymax, zmin), p(xmax, ymin, zmin)))
    
    # 2. TOP (Plano Z = zmax). Normal apunta hacia +Z.
    # Mirando desde arriba, antihorario es X+, luego Y+
    f_top    = geom.create_halfspace((p(xmin, ymin, zmax), p(xmax, ymin, zmax), p(xmin, ymax, zmax)))
    
    # 3. LEFT (Plano X = xmin). Normal apunta hacia -X.
    # Mirando desde la izquierda, antihorario es Z+, luego Y+
    f_left   = geom.create_halfspace((p(xmin, ymin, zmin), p(xmin, ymin, zmax), p(xmin, ymax, zmin)))
    
    # 4. RIGHT (Plano X = xmax). Normal apunta hacia +X.
    # Mirando desde la derecha, antihorario es Y+, luego Z+
    f_right  = geom.create_halfspace((p(xmax, ymin, zmin), p(xmax, ymax, zmin), p(xmax, ymin, zmax)))
    
    # 5. BACK (Plano Y = ymin). Normal apunta hacia -Y.
    # Mirando desde atrás, antihorario es X+, luego Z+
    f_back   = geom.create_halfspace((p(xmin, ymin, zmin), p(xmax, ymin, zmin), p(xmin, ymin, zmax)))
    
    # 6. FRONT (Plano Y = ymax). Normal apunta hacia +Y.
    # Mirando desde adelante, antihorario es Z+, luego X+
    f_front  = geom.create_halfspace((p(xmin, ymax, zmin), p(xmin, ymax, zmax), p(xmax, ymax, zmin)))
    
    return [f_bottom, f_top, f_left, f_right, f_back, f_front]

def run_pure_geometry_3d_test():
    geom3d = GeometryFactory[3]()
    pred3d = PredicatesFactory[3]()
    
    # Asumiendo que tenés tu Decorator3D listo, si no, usás tu checker principal
    checker = CoverageChecker3D(geometry=geom3d, predicates=pred3d)
    
    # 1. Nuestro Símplex Objetivo (Tetraedro en el centro del espacio)
    v1 = geom3d.create_point((2, 2, 2))
    v2 = geom3d.create_point((8, 2, 2))
    v3 = geom3d.create_point((5, 8, 2))
    v4 = geom3d.create_point((5, 5, 8))
    tetrahedron = geom3d.create_simplex((v1, v2, v3, v4))

    # Variables de estado que necesita envelope_check
    v_idx = {v1: False, v2: False, v3: False, v4: False}
    e_idx = {e: False for e in tetrahedron.get_edges()[0]} # o como devuelva tus aristas

    print("===========================================")
    
    # --- Escenario 1: Cobertura Total ---
    # Una sola caja gigante que envuelve completamente al tetraedro
    print("Ejecutando Escenario 1 (Debería dar IN - Todo OK)...")
    giant_box = create_mock_3d_box(geom3d, 0, 10, 0, 10, 0, 10)
    polytope_set_1 = [giant_box] # PolytopeMap con 1 solo politopo
    
    res1 = checker.envelope_check(tetrahedron, polytope_set_1, dict(v_idx), dict(e_idx))
    print(f"Resultado Escenario 1: {res1}")

    # --- Escenario 2: Falla C3 (Hueco en una cara) ---
    # Ponemos dos cajas a los costados, pero dejamos un pasillo vacío en el medio (X de 4 a 6).
    # Las aristas pueden estar cubiertas por otras cajas, pero el centro de la cara queda expuesto.
    print("\nEjecutando Escenario 2 (Debería fallar C3)...")
    box_left = create_mock_3d_box(geom3d, 0, 4, 0, 10, 0, 10)
    box_right = create_mock_3d_box(geom3d, 6, 10, 0, 10, 0, 10)
    polytope_set_2 = [box_left, box_right]
    
    res2 = checker.envelope_check(tetrahedron, polytope_set_2, dict(v_idx), dict(e_idx))
    print(f"Resultado Escenario 2: {res2}")

    # --- Escenario 3: Falla C4 (La "Caja Hueca") ---
    # Armamos 6 cajas finitas que forman las "paredes, techo y piso" del espacio.
    # El tetraedro está totalmente rodeado (C1, C2 y C3 pasan perfectas), 
    # pero el volumen central (por ej. X=5, Y=5, Z=5) está completamente vacío.
    # La intersección de 3 paredes internas va a generar un TPI adentro del tetraedro 
    # que ningún politopo cubre. ¡C4 obligada a fallar!
    print("\nEjecutando Escenario 3 (Debería fallar C4)...")
    p_floor = create_mock_3d_box(geom3d, 0, 10, 0, 10, 0, 3)
    p_ceil  = create_mock_3d_box(geom3d, 0, 10, 0, 10, 7, 10)
    p_left  = create_mock_3d_box(geom3d, 0, 3,  0, 10, 0, 10)
    p_right = create_mock_3d_box(geom3d, 7, 10, 0, 10, 0, 10)
    p_front = create_mock_3d_box(geom3d, 0, 10, 0, 3,  0, 10)
    p_back  = create_mock_3d_box(geom3d, 0, 10, 7, 10, 0, 10)
    
    polytope_set_3 = [p_floor, p_ceil, p_left, p_right, p_front, p_back]
    
    res3 = checker.envelope_check(tetrahedron, polytope_set_3, dict(v_idx), dict(e_idx))
    print(f"Resultado Escenario 3: {res3}")

if __name__ == "__main__":
    setup_logger()
    run_pure_geometry_3d_test()