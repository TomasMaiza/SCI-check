import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import ConvexHull
import matplotlib.patches as mpatches

# --- Importá tus clases reales acá ---
from geometry import GeometryFactory
from coverage_checker import CoverageChecker3D, PredicatesFactory
from geometry import PolytopeImp
from affine_system import SwitchedAffineSystem, AffineMode
from sci import SCIChecker

def plot_sci_result(dwell_time: float, K: int, is_covered: bool, target_polytope: 'PolytopeImp', subregions: list):
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # --- 1. Título ---
    title = f"K = {K} (h = {dwell_time})\nResultado de Cobertura: {is_covered}"
    ax.set_title(title, fontsize=16, pad=20)

    # --- 2. Politopo Objetivo (Caja sutil SIN telaraña) ---
    target_vertices = target_polytope.get_vertices() 
    if len(target_vertices) >= 4:
        hull_target = ConvexHull(target_vertices)
        target_faces = [target_vertices[simplex] for simplex in hull_target.simplices]
        # edgecolors='none' elimina las diagonales que ensuciaban la vista
        ax.add_collection3d(Poly3DCollection(target_faces, facecolors='red', linewidths=0, edgecolors='none', alpha=0.05))

    # --- 3. Subregiones y Leyenda ---
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown']
    legend_patches = []
    
    for i, halfspace_list in enumerate(subregions):
        if not halfspace_list:
            continue
            
        A_mat, b_vec = [], []
        for h in halfspace_list:
            n = h.get_normal()
            p = h.get_points()[0]
            A_mat.append([float(n[0]), float(n[1]), float(n[2])])
            b_vec.append(float(n[0]) * p.x + float(n[1]) * p.y + float(n[2]) * p.z)
            
        try:
            sub_poly = PolytopeImp(A=np.array(A_mat), b=np.array(b_vec))
            sub_vertices = sub_poly.get_vertices() 
            
            print(f"Debug Gráfico - Subregión {i}: Generó {len(sub_vertices)} vértices.")
            
            if sub_vertices is not None and len(sub_vertices) >= 4:
                # Usamos módulo por si el algoritmo genera más subregiones que colores
                color = colors[i % len(colors)] 
                hull_sub = ConvexHull(sub_vertices)
                sub_faces = [sub_vertices[simplex] for simplex in hull_sub.simplices]
                
                # Subregiones con opacidad y bordes negros limpios
                ax.add_collection3d(Poly3DCollection(sub_faces, facecolors=color, linewidths=0.8, edgecolors='black', alpha=0.5))
                
                # Evitamos duplicar entradas en la leyenda si hay múltiples subregiones del mismo modo
                label_name = f'Subregión {i}'
                if not any(p.get_label() == label_name for p in legend_patches):
                    legend_patches.append(mpatches.Patch(color=color, alpha=0.6, label=label_name))
            else:
                print(f"-> Omitida visualmente: La subregión {i} es plana o degenerada.")
                
        except Exception as e:
            print(f"Aviso: No se pudo graficar la subregión {i}. Error: {e}")

    # --- 4. Ajustes de Ejes ---
    mins = target_vertices.min(axis=0)
    maxs = target_vertices.max(axis=0)
    # Damos un pequeño margen para que el gráfico respire
    ax.set_xlim([mins[0] - 1, maxs[0] + 1])
    ax.set_ylim([mins[1] - 1, maxs[1] + 1])
    ax.set_zlim([mins[2] - 1, maxs[2] + 1])
    
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')
    ax.set_zlabel('Eje Z')
    
    if legend_patches:
        ax.legend(handles=legend_patches, loc='upper right')
        
    ax.view_init(elev=25, azim=45)
    plt.show()


def test_full_sci_checker():
    # 1. Inicializamos las fábricas 
    geom3d = GeometryFactory[3]()
    pred3d = PredicatesFactory[3]()
    
    # 2. Definimos el Politopo Objetivo (Caja de 0 a 10)
    A_poly = np.array([
        [-1.0,  0.0,  0.0],  [ 1.0,  0.0,  0.0],
        [ 0.0, -1.0,  0.0],  [ 0.0,  1.0,  0.0],
        [ 0.0,  0.0, -1.0],  [ 0.0,  0.0,  1.0]
    ])
    b_poly = np.array([0.0, 10.0, 0.0, 10.0, 0.0, 10.0])
    target_polytope = PolytopeImp(A=A_poly, b=b_poly) 

    # --- 3. SISTEMA DE 3 MODOS (Atractores en 3D) ---
    # Usamos matrices diagonales estables para que los volúmenes no colapsen a 2D
    A_base = np.array([
        [-1.0,  0.0,  0.0],
        [ 0.0, -1.0,  0.0],
        [ 0.0,  0.0, -1.0]
    ])
    
    # Modo 0: Tira hacia la esquina (2, 2, 2)
    mode0 = AffineMode(A=A_base, b=np.array([[2.0], [2.0], [2.0]]))
    
    # Modo 1: Tira hacia la esquina opuesta (8, 8, 2)
    mode1 = AffineMode(A=A_base, b=np.array([[8.0], [8.0], [2.0]]))
    
    # Modo 2: Tira hacia arriba en el medio (5, 5, 8)
    mode2 = AffineMode(A=A_base, b=np.array([[5.0], [5.0], [8.0]]))
    
    # Registramos los 3 modos en el diccionario
    modes_dict = {
        0: mode0.get_subsystem(),
        1: mode1.get_subsystem(),
        2: mode2.get_subsystem()
    }
    sas = SwitchedAffineSystem(modesDict=modes_dict) 
    # -----------------------------------------------

    # 4. Instanciamos el Orquestador
    print("Inicializando SCIChecker con 3 Modos...")
    checker = SCIChecker(
        geometry=geom3d,
        predicates=pred3d,
        coverageChecker=CoverageChecker3D, 
        polytope=target_polytope,
        sas=sas
    )

    # 5. Parámetros de prueba
    dwell_time = 0.5 
    K = 3

    # 6. Ejecución
    print("===========================================")
    print(f"Ejecutando sci_check con dwellTime={dwell_time}, K={K}...")
    is_covered, subregions = checker.sci_check(dwellTime=dwell_time, K=K)

    print("===========================================")
    print(f"RESULTADO DE COBERTURA: {'IN (Cubierto)' if is_covered else 'OUT (Huecos detectados)'}")
    print(f"Cantidad de subregiones generadas: {len(subregions)}")
    
    # 7. Graficamos
    if len(subregions) > 0:
        plot_sci_result(dwell_time, K, is_covered, target_polytope, subregions)
    else:
        print("No se generaron subregiones para graficar.")

if __name__ == "__main__":
    test_full_sci_checker()