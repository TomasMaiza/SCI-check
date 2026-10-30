import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.spatial import ConvexHull
from sci import SCIChecker
from coverage_checker import *
from geometry import Polytope, FloatPolytope
from coverage_checker import PredicatesFactory
from affine_system import SwitchedAffineSystem
from common import setup_logger
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import polytope as pc

def set_sci(polytope: FloatPolytope, sas: SwitchedAffineSystem):
  checker = SCIChecker(3, PredicatesFactory[3](), CoverageCheckerFactory[3], polytope, sas)
  return checker

def politopo():
  v = ((0.05, -0.5, 0.02), 
       (0.05, -0.5, -0.02),
       (0.05, 0.5, 0.02),
       (0.05, 0.5, -0.02),
       (-0.05, 0.5, -0.02),
       (-0.05, 0.5, 0.02),
       (-0.05, -0.5, -0.02),
       (-0.05, -0.5, 0.02))
  polytope = FloatPolytope(intDim=3, ambDim=3, vertices=v)
  return polytope

'''
def sistema():
  R_E = 100
  R = 25
  E = 24
  C1 = 50
  C2 = 25
  L = 10
  modos = {}
  modos[1] = (np.array([[-1/(R_E * C1), 0, 0], [0, -1/(R * C2), 1/C2], [0, -1/L, 0]]), 
              np.array([E/(R_E * C1), 0, 0]).reshape(-1, 1))
  modos[2] = (np.array([[-1/(R_E * C1), 0, -1/C1], [0, -1/(R * C2), 1/C2], [1/L, -1/L, 0]]), 
              np.array([E/(R_E * C1), 0, 0]).reshape(-1, 1))
  sas = SwitchedAffineSystem(modos)
  return sas

'''
def sistema():
    # 1. Parámetros con unidades correctas
    R_E = 100e-3
    R = 25
    E = 24
    C1 = 50e-6
    C2 = 25e-6
    L = 15.91e-3
    
    # Matrices A originales (dinámica)[cite: 3]
    A1 = np.array([[-1/(R_E * C1), 0, 0], 
                   [0, -1/(R * C2), 1/C2], 
                   [0, -1/L, 0]])
                   
    A2 = np.array([[-1/(R_E * C1), 0, -1/C1], 
                   [0, -1/(R * C2), 1/C2], 
                   [1/L, -1/L, 0]])
                   
    # Vector b original[cite: 3]
    b = np.array([E/(R_E * C1), 0, 0]).reshape(-1, 1)
    
    # 2. Cálculo del punto de equilibrio (xe)[cite: 3]
    x2e = 11.988  #[cite: 3]
    x1e = E - 0.5 * R_E * (x2e / R) #[cite: 3]
    x3e = x2e / R #[cite: 3]
    xe = np.array([x1e, x2e, x3e]).reshape(-1, 1)
    print(f"x1e: {x1e}, x3e: {x3e}")
    
    # 3. Traslación de los vectores afines al estado de error (be)[cite: 3]
    b1_e = A1 @ xe + b
    b2_e = A2 @ xe + b
    
    modos = {}
    modos[1] = (A1, b1_e)
    modos[2] = (A2, b2_e)
    sas = SwitchedAffineSystem(modos)
    
    return sas

def ejecutar_test(T: float, K: int):
  poly = politopo()
  sas = sistema()
  checker = set_sci(poly, sas)
  cov, subregions = checker.sci_check(T, K)
  print(f"El resultado es: {cov}")
  print_subregions_debug(subregions)
  plot_3d_scenario("Test 3D SIAM", poly, cov, subregions)
  #plot_projections_2d("Test 3D SIAM", poly, subregions)

def print_subregions_debug(subregions_map: list[Polytope]):
    print("\n" + "="*45)
    print(" DEBUG: DEFINICIÓN ALGEBRAICA DE SUBREGIONES")
    print("="*45)
    
    for mode_idx, p in enumerate(subregions_map):
        halfspace_list = p.get_halfspaces()
        if not halfspace_list:
            print(f"Modo {mode_idx}: Vacío (Sin semiespacios)")
            continue
            
        print(f"\nModo {mode_idx} ({len(halfspace_list)} semiespacios detectados):")
        
        for i, h in enumerate(halfspace_list):
            n = h.get_normal()
            p = h.get_points()[0]
            
            # --- EXTRACTOR DINÁMICO ---
            nx, ny, nz = n if isinstance(n, tuple) else (n[0], n[1], n[2])
            px, py, pz = p if isinstance(p, tuple) else (p[0], p[1], p[2])
            
            nx, ny, nz = float(nx), float(ny), float(nz)
            px, py, pz = float(px), float(py), float(pz)
            
            # Calculamos b = n * p
            b = nx * px + ny * py + nz * pz
            
            # Imprimimos la inecuación con 6 decimales para ver bien la escala
            print(f"  Cara {i:02d}: {nx:>9.6f}*x {ny:>+9.6f}*y {nz:>+9.6f}*z  <=  {b:>9.6f}")
            
    print("\n" + "="*45 + "\n")

def plot_3d_scenario(title: str, original_poly: Polytope, coverage_result: bool, subregions_map: list[Polytope]):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 1. Dibujamos la caja original usando sus vértices (fondo gris traslúcido)
    vertices_orig = original_poly.get_vertices()
    if vertices_orig is not None and len(vertices_orig) >= 4:
        hull_orig = ConvexHull(vertices_orig)
        faces_orig = [vertices_orig[s] for s in hull_orig.simplices]
        poly3d_orig = Poly3DCollection(faces_orig, alpha=0.1, facecolor='gray', edgecolor='black', linewidths=1)
        ax.add_collection3d(poly3d_orig)

    # Colores base imitando la paleta clásica
    colors = ['#1f77b4', '#ff7f0e', '#d62728', '#9467bd', '#2ca02c'] 

    # 2. Reconstruimos los polígonos cerrados de las subregiones
    for mode_idx, p in enumerate(subregions_map):
        halfspace_list = p.get_halfspaces()
        if not halfspace_list: 
            continue
            
        A_mat, b_vec = [], []
        for h in halfspace_list:
            # --- EXTRACTOR DINÁMICO ---
            n = h.get_normal()
            p = h.get_points()[0]
            
            nx, ny, nz = n if isinstance(n, tuple) else (n[0], n[1], n[2])
            px, py, pz = p if isinstance(p, tuple) else (p[0], p[1], p[2])
            
            # Convertimos a float para que scipy/numpy no exploten con los objetos Fraction
            nx, ny, nz = float(nx), float(ny), float(nz)
            px, py, pz = float(px), float(py), float(pz)
            
            A_mat.append([nx, ny, nz])
            b_vec.append(nx * px + ny * py + nz * pz)
            
        # 3. Armamos el politopo y extraemos sus vértices reales
        try:
            sub_poly = pc.Polytope(np.array(A_mat), np.array(b_vec))
            sub_vertices = pc.extreme(sub_poly)
            
            # Chequeo fundamental: que no sea un politopo vacío (None) o un plano degenerado (< 4)
            if sub_vertices is not None and len(sub_vertices) >= 4:
                hull = ConvexHull(sub_vertices)
                faces = [sub_vertices[s] for s in hull.simplices]
                
                # Creamos el parche relleno 3D
                poly3d = Poly3DCollection(
                    faces, 
                    alpha=0.6, 
                    facecolor=colors[mode_idx % len(colors)], 
                    edgecolor='black', 
                    linewidths=0.5,
                    label=f'Modo {mode_idx}'
                )
                ax.add_collection3d(poly3d)
                
                # Hack para que la leyenda en 3D funcione (Poly3DCollection a veces falla con labels)
                poly3d._facecolors2d = poly3d._facecolor3d
                poly3d._edgecolors2d = poly3d._edgecolor3d
                
        except Exception as e:
            print(f"Aviso silencioso: No se graficó la subregión {mode_idx}. {e}")

    # Configuraciones estéticas adaptadas al tamaño de tu sistema SIAM
    ax.set_title(f"{title}\nResultado de Cobertura: {coverage_result}", fontsize=14)
    # Ajustamos los límites a las coordenadas de los vértices que definiste en tu test
    ax.set_xlim([-0.06, 0.06]) 
    ax.set_ylim([-0.6, 0.6])
    ax.set_zlim([-0.03, 0.03])
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

    # 1. Extraer vértices del politopo original
    vertices_orig = np.array(original_poly.get_vertices(), dtype=float)
    if vertices_orig is None or len(vertices_orig) == 0:
        print("El politopo original no tiene vértices para proyectar.")
        return

    # Definimos los 3 planos: (índice_eje_horizontal, índice_eje_vertical, label_x, label_y, título)
    planes = [
        (0, 1, 'Eje X (Voltaje C1)', 'Eje Y (Voltaje C2)', 'Plano XY'),
        (0, 2, 'Eje X (Voltaje C1)', 'Eje Z (Corriente L)', 'Plano XZ'),
        (1, 2, 'Eje Y (Voltaje C2)', 'Eje Z (Corriente L)', 'Plano YZ')
    ]
    
    colors = ['#1f77b4', '#ff7f0e', '#d62728', '#9467bd', '#2ca02c']

    for i, (dim1, dim2, xlabel, ylabel, plane_name) in enumerate(planes):
        ax = axes[i]
        
        # 2. Proyección 2D del Politopo Original
        V_orig_2d = vertices_orig[:, [dim1, dim2]]
        try:
            hull_orig = ConvexHull(V_orig_2d)
            # Dibujamos la sombra original (gris claro con borde rojo)
            poly_patch = patches.Polygon(
                V_orig_2d[hull_orig.vertices], closed=True, 
                facecolor='gray', alpha=0.15, edgecolor='red', linewidth=2, label='Original'
            )
            ax.add_patch(poly_patch)
        except Exception as e:
            print(f"No se pudo proyectar el original en {plane_name}: {e}")
        
        # 3. Proyección 2D de las Subregiones
        for mode_idx, p in enumerate(subregions_map):
            halfspace_list = p.get_halfspaces()
            if not halfspace_list:
                continue
            
            # Reconstrucción de la matriz A y b para sacar los vértices de la subregión
            A_mat, b_vec = [], []
            for h in halfspace_list:
                n = h.get_normal()
                pt = h.get_points()[0]
                
                nx, ny, nz = n if isinstance(n, tuple) else (n[0], n[1], n[2])
                px, py, pz = pt if isinstance(pt, tuple) else (pt[0], pt[1], pt[2])
                nx, ny, nz = float(nx), float(ny), float(nz)
                px, py, pz = float(px), float(py), float(pz)
                
                A_mat.append([nx, ny, nz])
                b_vec.append(nx * px + ny * py + nz * pz)
                
            try:
                sub_poly = pc.Polytope(np.array(A_mat), np.array(b_vec))
                sub_vertices = pc.extreme(sub_poly)
                
                if sub_vertices is not None and len(sub_vertices) >= 3:
                    # Descartamos el tercer eje para tener la proyección 2D
                    V_sub_2d = sub_vertices[:, [dim1, dim2]]
                    
                    # Qhull a veces falla si los puntos proyectados quedan alineados perfectamente (una línea)
                    # El qhull_options='QJ' previene crasheos agregando ruido infinitesimal si eso pasa.
                    hull_sub = ConvexHull(V_sub_2d, qhull_options='QJ')
                    
                    poly_patch = patches.Polygon(
                        V_sub_2d[hull_sub.vertices], closed=True, 
                        facecolor=colors[mode_idx % len(colors)], alpha=0.5, 
                        edgecolor=colors[mode_idx % len(colors)], linewidth=1.5, 
                        label=f'Modo {mode_idx}'
                    )
                    ax.add_patch(poly_patch)
            except Exception as e:
                pass # Ignoramos silenciosamente si la subregión es vacía o degenerada en este plano
        
        # 4. Ajustar los márgenes de los ejes dinámicamente
        orig_min_1, orig_max_1 = np.min(V_orig_2d[:, 0]), np.max(V_orig_2d[:, 0])
        orig_min_2, orig_max_2 = np.min(V_orig_2d[:, 1]), np.max(V_orig_2d[:, 1])
        
        margin1 = (orig_max_1 - orig_min_1) * 0.15 if (orig_max_1 - orig_min_1) != 0 else 0.1
        margin2 = (orig_max_2 - orig_min_2) * 0.15 if (orig_max_2 - orig_min_2) != 0 else 0.1
        
        ax.set_xlim([orig_min_1 - margin1, orig_max_1 + margin1])
        ax.set_ylim([orig_min_2 - margin2, orig_max_2 + margin2])
        
        # Textos y Leyendas
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(plane_name)
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Evitar duplicar leyendas por parche
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='best', fontsize=9)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
  setup_logger()
  ejecutar_test(T = 20 * 1e-6, K = 30)