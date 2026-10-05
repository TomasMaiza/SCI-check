import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.spatial import ConvexHull
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import polytope as pc

# Importaciones de tu arquitectura
from sci import SCIChecker
from geometry import ConcretePolytope, Polytope
from coverage_checker import PredicatesFactory, CoverageCheckerFactory
from affine_system import SwitchedAffineSystem
from common import setup_logger

def politopo():
    # 1. Definimos una caja perfecta de [-1, 1] en todos los ejes
    v = (( 1.0,  1.0,  1.0),
         ( 1.0,  1.0, -1.0),
         ( 1.0, -1.0,  1.0),
         ( 1.0, -1.0, -1.0),
         (-1.0,  1.0,  1.0),
         (-1.0,  1.0, -1.0),
         (-1.0, -1.0,  1.0),
         (-1.0, -1.0, -1.0))
    polytope = ConcretePolytope(intDim=3, ambDim=3, vertices=v)
    return polytope

def sistema():
    # 2. Matriz A estable y desacoplada para que las regiones crezcan fluidamente
    A = np.array([[-2.0,  0.0,  0.0],
                  [ 0.0, -2.0,  0.0],
                  [ 0.0,  0.0, -2.0]])

    # 3. 8 Modos: 1 punto de equilibrio (atractor) en cada octante del espacio 3D
    centros = [
        ( 3.0,  3.0,  3.0),  # Octante 1
        (-3.0,  3.0,  3.0),  # Octante 2
        ( 3.0, -3.0,  3.0),  # Octante 3
        (-3.0, -3.0,  3.0),  # Octante 4
        ( 3.0,  3.0, -3.0),  # Octante 5
        (-3.0,  3.0, -3.0),  # Octante 6
        ( 3.0, -3.0, -3.0),  # Octante 7
        (-3.0, -3.0, -3.0)   # Octante 8
    ]

    modos = {}
    for i, c in enumerate(centros):
        xe = np.array(c).reshape(-1, 1)
        # Calculamos el vector b correspondiente para que el equilibrio caiga en 'xe'
        b = -A @ xe 
        modos[i] = (A, b)

    sas = SwitchedAffineSystem(modos)
    return sas

def ejecutar_test(T: float, K: int):
    poly = politopo()
    sas = sistema()
    
    # Instanciamos usando la misma firma que tu test SIAM
    checker = SCIChecker(3, PredicatesFactory[3](), CoverageCheckerFactory[3], poly, sas)
    cov, subregions = checker.sci_check(T, K)
    
    print("\n" + "="*50)
    print(f" RESULTADO FINAL DE COBERTURA: {cov}")
    print("="*50 + "\n")
    
    # Usamos tus mismas funciones de visualización
    plot_3d_scenario("Test 3D - 8 Octantes", poly, cov, subregions)
    plot_projections_2d("Test 3D - 8 Octantes", poly, subregions)

# =====================================================================
# PEGAR AQUÍ TUS FUNCIONES DE PLOTEO (plot_3d_scenario y plot_projections_2d)
# EXACTAMENTE COMO LAS TENÉS EN test_3d_siam.py
# =====================================================================
def plot_3d_scenario(title: str, original_poly: Polytope, coverage_result: bool, subregions_map: list[Polytope]):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    vertices_orig = original_poly.get_vertices()
    if vertices_orig is not None and len(vertices_orig) >= 4:
        hull_orig = ConvexHull(vertices_orig)
        faces_orig = [vertices_orig[s] for s in hull_orig.simplices]
        poly3d_orig = Poly3DCollection(faces_orig, alpha=0.05, facecolor='gray', edgecolor='black', linewidths=2)
        ax.add_collection3d(poly3d_orig)

    colors = ['#1f77b4', '#ff7f0e', '#d62728', '#9467bd', '#2ca02c', '#8c564b', '#e377c2', '#7f7f7f'] 

    for mode_idx, p in enumerate(subregions_map):
        halfspace_list = p.get_halfspaces()
        if not halfspace_list: continue
            
        A_mat, b_vec = [], []
        for h in halfspace_list:
            n = h.get_normal()
            p = h.get_points()[0]
            nx, ny, nz = n if isinstance(n, tuple) else (n[0], n[1], n[2])
            px, py, pz = p if isinstance(p, tuple) else (p[0], p[1], p[2])
            nx, ny, nz = float(nx), float(ny), float(nz)
            px, py, pz = float(px), float(py), float(pz)
            A_mat.append([nx, ny, nz])
            b_vec.append(nx * px + ny * py + nz * pz)
            
        try:
            sub_poly = pc.Polytope(np.array(A_mat), np.array(b_vec))
            sub_vertices = pc.extreme(sub_poly)
            if sub_vertices is not None and len(sub_vertices) >= 4:
                hull = ConvexHull(sub_vertices)
                faces = [sub_vertices[s] for s in hull.simplices]
                poly3d = Poly3DCollection(faces, alpha=0.6, facecolor=colors[mode_idx % len(colors)], edgecolor='black', linewidths=0.5, label=f'Modo {mode_idx}')
                ax.add_collection3d(poly3d)
                poly3d._facecolors2d = poly3d._facecolor3d
                poly3d._edgecolors2d = poly3d._edgecolor3d
        except Exception:
            pass

    ax.set_title(f"{title}\nResultado de Cobertura: {coverage_result}", fontsize=14)
    # Ajustamos los límites de la cámara a la nueva caja [-1, 1]
    ax.set_xlim([-1.5, 1.5]) 
    ax.set_ylim([-1.5, 1.5])
    ax.set_zlim([-1.5, 1.5])
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')
    ax.set_zlabel('Eje Z')
    
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper right')
    plt.show()

def plot_projections_2d(title: str, original_poly: Polytope, subregions_map: list[Polytope]):
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(f"{title} - Proyecciones a Planos 2D", fontsize=16)

    vertices_orig = np.array(original_poly.get_vertices(), dtype=float)
    planes = [(0, 1, 'Eje X', 'Eje Y', 'Plano XY'), (0, 2, 'Eje X', 'Eje Z', 'Plano XZ'), (1, 2, 'Eje Y', 'Eje Z', 'Plano YZ')]
    colors = ['#1f77b4', '#ff7f0e', '#d62728', '#9467bd', '#2ca02c', '#8c564b', '#e377c2', '#7f7f7f']

    for i, (dim1, dim2, xlabel, ylabel, plane_name) in enumerate(planes):
        ax = axes[i]
        V_orig_2d = vertices_orig[:, [dim1, dim2]]
        try:
            hull_orig = ConvexHull(V_orig_2d)
            poly_patch = patches.Polygon(V_orig_2d[hull_orig.vertices], closed=True, facecolor='gray', alpha=0.15, edgecolor='red', linewidth=2, label='Original')
            ax.add_patch(poly_patch)
        except: pass
        
        for mode_idx, p in enumerate(subregions_map):
            halfspace_list = p.get_halfspaces()
            if not halfspace_list: continue
            
            A_mat, b_vec = [], []
            for h in halfspace_list:
                n = h.get_normal()
                pt = h.get_points()[0]
                nx, ny, nz = float(n[0]), float(n[1]), float(n[2])
                px, py, pz = float(pt[0]), float(pt[1]), float(pt[2])
                A_mat.append([nx, ny, nz])
                b_vec.append(nx * px + ny * py + nz * pz)
                
            try:
                sub_poly = pc.Polytope(np.array(A_mat), np.array(b_vec))
                sub_vertices = pc.extreme(sub_poly)
                if sub_vertices is not None and len(sub_vertices) >= 3:
                    V_sub_2d = sub_vertices[:, [dim1, dim2]]
                    hull_sub = ConvexHull(V_sub_2d, qhull_options='QJ')
                    poly_patch = patches.Polygon(V_sub_2d[hull_sub.vertices], closed=True, facecolor=colors[mode_idx % len(colors)], alpha=0.5, edgecolor=colors[mode_idx % len(colors)], linewidth=1.5, label=f'Modo {mode_idx}')
                    ax.add_patch(poly_patch)
            except: pass
        
        ax.set_xlim([-1.5, 1.5])
        ax.set_ylim([-1.5, 1.5])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(plane_name)
        ax.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    setup_logger()
    # Con K=10 las 8 regiones ya van a ser lo suficientemente masivas 
    # para cubrir toda la caja [-1, 1]^3.
    ejecutar_test(T = 0.1, K = 10)