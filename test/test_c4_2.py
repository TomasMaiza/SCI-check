import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.spatial import ConvexHull
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import itertools

from geometry import ConcretePolytope
from coverage_checker import CoverageChecker3D
from coverage_checker.predicates import PredicatesFactory
from common import setup_logger, IN, OUT

def generate_hardcoded_test():
    # 1. Politopo Base: Un cubo perfecto de [-1, 1]
    base_verts = [
        ( 1,  1,  1), ( 1,  1, -1), ( 1, -1,  1), ( 1, -1, -1),
        (-1,  1,  1), (-1,  1, -1), (-1, -1,  1), (-1, -1, -1)
    ]
    base_poly = ConcretePolytope(intDim=3, ambDim=3, vertices=base_verts)

    # 2. Subregiones: 8 Octantes perfectos
    subregions = []
    ejes = [[(0.0, 1.0), (-1.0, 0.0)]] * 3  
    
    for rangos_x, rangos_y, rangos_z in itertools.product(*ejes):
        sub_verts = []
        for x in rangos_x:
            for y in rangos_y:
                for z in rangos_z:
                    sub_verts.append((x, y, z))
        
        sub_poly = ConcretePolytope(intDim=3, ambDim=3, vertices=sub_verts)
        subregions.append(sub_poly)

    return base_poly, subregions

def plot_3d_octantes(title: str, base_poly, coverage_result, subregions):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Colores para los 8 octantes
    colors = ['#1f77b4', '#ff7f0e', '#d62728', '#9467bd', 
              '#2ca02c', '#8c564b', '#e377c2', '#7f7f7f']
              
    # 1. Graficar el cubo base original (Alambre / Wireframe)
    base_verts = np.array(base_poly.get_vertices())
    hull_base = ConvexHull(base_verts)
    faces_base = [base_verts[s] for s in hull_base.simplices]
    poly3d_base = Poly3DCollection(faces_base, alpha=0.05, facecolor='gray', 
                                   edgecolor='black', linewidths=2)
    ax.add_collection3d(poly3d_base)

    # 2. Graficar los 8 octantes
    for i, sub in enumerate(subregions):
        sub_verts = np.array(sub.get_vertices())
        hull_sub = ConvexHull(sub_verts)
        faces_sub = [sub_verts[s] for s in hull_sub.simplices]
        
        poly3d_sub = Poly3DCollection(
            faces_sub, 
            alpha=0.7, # Alta opacidad para ver cómo encastran
            facecolor=colors[i % len(colors)], 
            edgecolor='white', # Borde blanco para resaltar las fronteras entre ellos
            linewidths=1.0,
            label=f'Octante {i+1}'
        )
        ax.add_collection3d(poly3d_sub)
        
        # Parche para la leyenda 3D en matplotlib
        poly3d_sub._facecolors2d = poly3d_sub._facecolor3d
        poly3d_sub._edgecolors2d = poly3d_sub._edgecolor3d

    ax.set_title(f"{title}\nResultado de Cobertura SCI: {coverage_result}", fontsize=14)
    ax.set_xlim([-1.5, 1.5])
    ax.set_ylim([-1.5, 1.5])
    ax.set_zlim([-1.5, 1.5])
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')
    ax.set_zlabel('Eje Z')
    
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='center left', bbox_to_anchor=(1, 0.5))
        
    plt.tight_layout()
    plt.show()

def plot_projections_2d_octantes(base_poly, subregions):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Proyecciones 2D (Cortes del Cubo)", fontsize=16)

    base_verts = np.array(base_poly.get_vertices())
    planes = [(0, 1, 'X', 'Y', 'Plano XY'), 
              (0, 2, 'X', 'Z', 'Plano XZ'), 
              (1, 2, 'Y', 'Z', 'Plano YZ')]
    colors = ['#1f77b4', '#ff7f0e', '#d62728', '#9467bd', 
              '#2ca02c', '#8c564b', '#e377c2', '#7f7f7f']

    for i, (dim1, dim2, xlabel, ylabel, plane_name) in enumerate(planes):
        ax = axes[i]
        
        # Sombra original
        V_base_2d = base_verts[:, [dim1, dim2]]
        hull_base = ConvexHull(V_base_2d)
        poly_patch = patches.Polygon(V_base_2d[hull_base.vertices], closed=True, 
                                     facecolor='none', edgecolor='black', 
                                     linewidth=3, linestyle='--', zorder=10)
        ax.add_patch(poly_patch)
        
        # Subregiones
        for idx, sub in enumerate(subregions):
            sub_verts = np.array(sub.get_vertices())
            V_sub_2d = sub_verts[:, [dim1, dim2]]
            
            # Usamos QJ para que scipy no explote si la proyección colapsa puntos
            hull_sub = ConvexHull(V_sub_2d, qhull_options='QJ')
            poly_patch = patches.Polygon(
                V_sub_2d[hull_sub.vertices], 
                closed=True, 
                facecolor=colors[idx % len(colors)], 
                alpha=0.5, 
                edgecolor='black', 
                linewidth=1,
                label=f'Oct. {idx+1}'
            )
            ax.add_patch(poly_patch)
            
        ax.set_xlim([-1.5, 1.5])
        ax.set_ylim([-1.5, 1.5])
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(plane_name)
        ax.grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    setup_logger()
    
    print("1. Construyendo el cubo y los 8 octantes perfectos...")
    base_poly, subregions = generate_hardcoded_test()
    
    print("2. Evaluando algoritmos SCI...")
    predicates = PredicatesFactory[3]() 
    checker = CoverageChecker3D(predicates)
    
    result = checker.envelope_check(base_poly, subregions)
    
    print("\n" + "="*40)
    print(f" COBERTURA FINAL: {result}")
    plot_3d_octantes("test c4", base_poly, result, subregions)