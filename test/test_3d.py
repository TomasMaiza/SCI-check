import numpy as np
from coverage_checker import CoverageChecker3D, PredicatesFactory
from geometry import GeometryFactory, Geometry3d
from common import PolytopeMap, VerticesIndex, EdgesIndex, OrientResult, setup_logger
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import ConvexHull
import itertools

def create_mock_3d_box(geom, xmin, xmax, ymin, ymax, zmin, zmax) -> tuple:
    """
    Retorna una tupla con dos elementos:
    1. halfspaces: Lista matemática de 6 Halfspace3D para el validador C++.
    2. vertices_plot: Array de 8 vértices para dibujar la caja sólida completa.
    """
    def p(x, y, z): return geom.create_point((x, y, z))
    
    # 1. Matemática (Las 6 caras en antihorario)
    f_bottom = geom.create_halfspace((p(xmin, ymin, zmin), p(xmin, ymax, zmin), p(xmax, ymin, zmin)))
    f_top    = geom.create_halfspace((p(xmin, ymin, zmax), p(xmax, ymin, zmax), p(xmin, ymax, zmax)))
    f_left   = geom.create_halfspace((p(xmin, ymin, zmin), p(xmin, ymin, zmax), p(xmin, ymax, zmin)))
    f_right  = geom.create_halfspace((p(xmax, ymin, zmin), p(xmax, ymax, zmin), p(xmax, ymin, zmax)))
    f_back   = geom.create_halfspace((p(xmin, ymin, zmin), p(xmax, ymin, zmin), p(xmin, ymin, zmax)))
    f_front  = geom.create_halfspace((p(xmin, ymax, zmin), p(xmin, ymax, zmax), p(xmax, ymax, zmin)))
    
    halfspaces = [f_bottom, f_top, f_left, f_right, f_back, f_front]

    # 2. Visualización (Generamos los 8 vértices de la caja)
    vertices_plot = np.array(list(itertools.product([xmin, xmax], [ymin, ymax], [zmin, zmax])))
    
    return halfspaces, vertices_plot

def plot_solid_3d_scenario(title: str, tetrahedron, polytope_visuals: list):
    """Grafica el tetraedro y las cajas cobertores usando ConvexHull para mallas cerradas."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 1. Dibujar el Tetraedro (Rojo)
    v1, v2, v3, v4 = tetrahedron.get_vertices()
    tet_faces = [
        [(v1.x, v1.y, v1.z), (v2.x, v2.y, v2.z), (v3.x, v3.y, v3.z)],
        [(v1.x, v1.y, v1.z), (v2.x, v2.y, v2.z), (v4.x, v4.y, v4.z)],
        [(v1.x, v1.y, v1.z), (v3.x, v3.y, v3.z), (v4.x, v4.y, v4.z)],
        [(v2.x, v2.y, v2.z), (v3.x, v3.y, v3.z), (v4.x, v4.y, v4.z)]
    ]
    ax.add_collection3d(Poly3DCollection(tet_faces, facecolors='red', linewidths=1, edgecolors='darkred', alpha=0.8))

    # 2. Dibujar las Cajas usando ConvexHull (Colores translúcidos)
    colors = ['cyan', 'green', 'orange', 'purple', 'blue', 'yellow']
    
    for i, vertices in enumerate(polytope_visuals):
        color = colors[i % len(colors)]
        # ConvexHull envuelve los 8 vértices y arma la caja sólida perfecta
        hull = ConvexHull(vertices)
        faces = [vertices[simplex] for simplex in hull.simplices]
        
        ax.add_collection3d(Poly3DCollection(faces, facecolors=color, linewidths=0.5, edgecolors='black', alpha=0.15))

    ax.set_xlim([0, 10])
    ax.set_ylim([0, 10])
    ax.set_zlim([0, 10])
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')
    ax.set_zlabel('Eje Z')
    ax.set_title(title, fontsize=14, pad=20)
    ax.view_init(elev=20, azim=45)
    plt.show()

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
    e_idx = {e: False for e in tetrahedron.get_all_edges()} # o como devuelva tus aristas

    print("===========================================")
    
    # --- Escenario 1: Cobertura Total ---
    print("Ejecutando Escenario 1 (Debería dar IN - Todo OK)...")
    # Desempaquetamos la tupla: matemática por un lado, vértices visuales por otro
    giant_box_math, giant_box_vis = create_mock_3d_box(geom3d, 0, 10, 0, 10, 0, 10)
    
    polytope_set_1 = [giant_box_math] # Para el validador
    visuals_1 = [giant_box_vis]       # Para el graficador
    
    res1 = checker.envelope_check(tetrahedron, polytope_set_1, dict(v_idx), dict(e_idx))
    print(f"Resultado Escenario 1: {res1}")
    plot_solid_3d_scenario("Escenario 1: Todo OK", tetrahedron, visuals_1)

    # --- Escenario 2: Falla C3 (Hueco en una cara) ---
    print("\nEjecutando Escenario 2 (Debería fallar C3)...")
    box_left_math, box_left_vis = create_mock_3d_box(geom3d, 0, 4, 0, 10, 0, 10)
    box_right_math, box_right_vis = create_mock_3d_box(geom3d, 6, 10, 0, 10, 0, 10)
    
    polytope_set_2 = [box_left_math, box_right_math]
    visuals_2 = [box_left_vis, box_right_vis]
    
    res2 = checker.envelope_check(tetrahedron, polytope_set_2, dict(v_idx), dict(e_idx))
    print(f"Resultado Escenario 2: {res2}")
    plot_solid_3d_scenario("Escenario 2: Falla C3 (Pasillo central hueco)", tetrahedron, visuals_2)

    # --- Escenario 3: Falla C4 (La "Caja Hueca") ---
    print("\nEjecutando Escenario 3 (Debería fallar C4)...")
    p_floor_math, p_floor_vis = create_mock_3d_box(geom3d, 0, 10, 0, 10, 0, 3)
    p_ceil_math, p_ceil_vis   = create_mock_3d_box(geom3d, 0, 10, 0, 10, 7, 10)
    p_left_math, p_left_vis   = create_mock_3d_box(geom3d, 0, 3,  0, 10, 0, 10)
    p_right_math, p_right_vis = create_mock_3d_box(geom3d, 7, 10, 0, 10, 0, 10)
    p_front_math, p_front_vis = create_mock_3d_box(geom3d, 0, 10, 0, 3,  0, 10)
    p_back_math, p_back_vis   = create_mock_3d_box(geom3d, 0, 10, 7, 10, 0, 10)
    
    polytope_set_3 = [p_floor_math, p_ceil_math, p_left_math, p_right_math, p_front_math, p_back_math]
    visuals_3 = [p_floor_vis, p_ceil_vis, p_left_vis, p_right_vis, p_front_vis, p_back_vis]
    
    res3 = checker.envelope_check(tetrahedron, polytope_set_3, dict(v_idx), dict(e_idx))
    print(f"Resultado Escenario 3: {res3}")
    plot_solid_3d_scenario("Escenario 3: Falla C4 (Interior hueco)", tetrahedron, visuals_3)

if __name__ == "__main__":
    setup_logger()
    run_pure_geometry_3d_test()