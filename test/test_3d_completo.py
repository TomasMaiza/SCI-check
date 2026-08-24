import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import ConvexHull

# --- Importá tus clases reales acá ---
from geometry import GeometryFactory
from coverage_checker import CoverageChecker3D, PredicatesFactory
from geometry import PolytopeImp
from affine_system import SwitchedAffineSystem, AffineMode
from sci import SCIChecker

def plot_sci_result(title: str, target_polytope: 'PolytopeImp', subregions: list['PolytopeImp']):
    """Grafica el politopo objetivo y las subregiones generadas por el sistema dinámico."""
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # 1. Dibujar el Politopo Objetivo (Rojo translúcido)
    # Usamos get_vertices() que retorna el ndarray de la librería polytope
    target_vertices = target_polytope.get_vertices() 
    if len(target_vertices) >= 4:
        hull_target = ConvexHull(target_vertices)
        target_faces = [target_vertices[simplex] for simplex in hull_target.simplices]
        ax.add_collection3d(Poly3DCollection(target_faces, facecolors='red', linewidths=2, edgecolors='darkred', alpha=0.1))

    # 2. Dibujar las Subregiones (Colores sólidos)
    colors = ['cyan', 'green', 'orange', 'purple', 'blue', 'yellow', 'magenta']
    
    for i, sub_poly in enumerate(subregions):
        sub_vertices = sub_poly.get_vertices() 
        if len(sub_vertices) >= 4: # Necesitamos al menos 4 puntos para un volumen 3D
            color = colors[i % len(colors)]
            hull_sub = ConvexHull(sub_vertices)
            sub_faces = [sub_vertices[simplex] for simplex in hull_sub.simplices]
            
            # Las dibujamos con un poco más de opacidad para ver cómo "llenan" el espacio
            ax.add_collection3d(Poly3DCollection(sub_faces, facecolors=color, linewidths=0.5, edgecolors='black', alpha=0.4))

    # Ajustamos los límites de la cámara según los vértices del politopo objetivo
    mins = target_vertices.min(axis=0)
    maxs = target_vertices.max(axis=0)
    ax.set_xlim([mins[0] - 1, maxs[0] + 1])
    ax.set_ylim([mins[1] - 1, maxs[1] + 1])
    ax.set_zlim([mins[2] - 1, maxs[2] + 1])
    
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')
    ax.set_zlabel('Eje Z')
    ax.set_title(title, fontsize=16, pad=20)
    ax.view_init(elev=25, azim=45)
    plt.show()

def test_full_sci_checker():
    # 1. Inicializamos las fábricas de geometría y predicados
    geom3d = GeometryFactory[3]()
    pred3d = PredicatesFactory[3]()
    
    # 2. Definimos el Politopo Objetivo (Una caja de 0 a 10 en X, Y, Z)
    # Proveemos A y b para inicializar el PolytopeImp
    A_poly = np.array([
        [-1.0,  0.0,  0.0],  # -x <= 0
        [ 1.0,  0.0,  0.0],  #  x <= 10
        [ 0.0, -1.0,  0.0],  # -y <= 0
        [ 0.0,  1.0,  0.0],  #  y <= 10
        [ 0.0,  0.0, -1.0],  # -z <= 0
        [ 0.0,  0.0,  1.0]   #  z <= 10
    ])
    b_poly = np.array([0.0, 10.0, 0.0, 10.0, 0.0, 10.0])
    target_polytope = PolytopeImp(A=A_poly, b=b_poly) 

    # 3. Definimos el Sistema Afín Conmutado (SAS)
    # Creamos una matriz A cuadrada (n x n) y un vector b columna (n, 1)
    # Simulamos un modo estable hacia el origen
    A_mode1 = np.array([
        [-1.0,  0.0,  0.0],
        [ 0.0, -1.0,  0.0],
        [ 0.0,  0.0, -1.0]
    ])
    b_mode1 = np.array([[5.0], [5.0], [5.0]]) 
    
    # Instanciamos el modo
    mode1 = AffineMode(A=A_mode1, b=b_mode1) 
    
    # Armamos el diccionario de modos y pasamos al sistema
    modes_dict = {1: mode1.get_subsystem()} 
    sas = SwitchedAffineSystem(modesDict=modes_dict) 

    # 4. Instanciamos el Orquestador
    print("Inicializando SCIChecker...")
    checker = SCIChecker(
        geometry=geom3d,
        predicates=pred3d,
        coverageChecker=CoverageChecker3D, 
        polytope=target_polytope,
        sas=sas
    )

    # 5. Parámetros de prueba
    dwell_time = 0.5 
    K = 3 # Nivel de profundidad del algoritmo

    # 6. ¡Ejecución!
    print("===========================================")
    print(f"Ejecutando sci_check con dwellTime={dwell_time}, K={K}...")
    is_covered, subregions = checker.sci_check(dwellTime=dwell_time, K=K)

    print("===========================================")
    print(f"RESULTADO DE COBERTURA: {'IN (Cubierto)' if is_covered else 'OUT (Huecos detectados)'}")
    print(f"Cantidad de subregiones generadas: {len(subregions)}")
    
    # 7. Graficamos el resultado
    if len(subregions) > 0:
        plot_sci_result("Test de Integración SCIChecker 3D", target_polytope, subregions)
    else:
        print("No se generaron subregiones para graficar.")

if __name__ == "__main__":
    test_full_sci_checker()