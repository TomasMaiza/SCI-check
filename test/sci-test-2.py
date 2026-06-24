import sys
import os

# 1. Calculamos la ruta absoluta a la carpeta raíz del proyecto (subiendo un nivel '..')
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 2. Inyectamos esa ruta en el radar de búsqueda de Python
sys.path.insert(0, ruta_raiz)

import polytope as pc
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from scipy.spatial import ConvexHull

# --- IMPORTA TUS CLASES ACÁ ---
from geometry.geometry_2d import Geometry2d
from coverage_checker.predicates_2d import Predicates2d
# Asumo que SCIChecker está en un archivo sci.py o similar:
from sci import SCIChecker 
from common.types import PolytopeMap

def crear_caja(xmin: float, xmax: float, ymin: float, ymax: float) -> pc.Polytope:
    """
    Crea un politopo rectangular (Bounding Box) a partir de sus límites
    utilizando la representación H (Semiespacios Ax <= b).
    """
    A = np.array([
        [-1.0,  0.0],
        [ 1.0,  0.0],
        [ 0.0, -1.0],
        [ 0.0,  1.0]
    ])
    b = np.array([-xmin, xmax, -ymin, ymax])
    
    return pc.Polytope(A, b)

def extraer_semiespacios(poly: pc.Polytope, fabrica: Geometry2d) -> set:
    """Extrae los vértices del politopo, los ordena y crea Halfspace2D exactos."""
    caras = set()
    
    # poly.V devuelve las coordenadas crudas de los vértices
    vertices = pc.extreme(poly)
    
    # ConvexHull encuentra el perímetro y ordena los vértices en sentido antihorario (CCW)
    hull = ConvexHull(vertices)
    indices_ordenados = hull.vertices 
    cantidad_vertices = len(indices_ordenados)
    
    for i in range(cantidad_vertices):
        # Tomamos el vértice actual y el siguiente (con módulo para cerrar el ciclo)
        idx_actual = indices_ordenados[i]
        idx_siguiente = indices_ordenados[(i + 1) % cantidad_vertices]
        
        v_actual = vertices[idx_actual]
        v_siguiente = vertices[idx_siguiente]
        
        # Creamos los objetos Point2D usando tu fábrica
        # Usamos los mismos índices del hull como ID para mantener un rastro
        p1 = fabrica.create_point((float(v_actual[0]), float(v_actual[1])))
        p2 = fabrica.create_point((float(v_siguiente[0]), float(v_siguiente[1])))
        
        # Creamos el semiespacio a partir de los dos puntos
        cara = fabrica.create_halfspace((p1, p2))
        caras.add(cara)
        
    return caras

def graficar_escenario(main_poly, subregions, titulo, ax):
    """Función auxiliar para graficar usando matplotlib"""
    # Dibujamos el politopo principal (fondo gris)
    ax.add_patch(patches.Rectangle((0, 0), 4, 4, linewidth=2, edgecolor='black', 
                                   facecolor='lightgray', alpha=0.5, label='Politopo Malla'))
    
    # Dibujamos las subregiones encima con colores
    colores = ['blue', 'green', 'orange']
    for i, sub_box in enumerate(subregions):
        # Extraemos los límites de la caja para graficar
        # bounds devuelve (xmin, xmax, ymin, ymax)
        # Extraemos los límites de la caja para graficar
        bounds = sub_box.bounding_box
        xmin, ymin = bounds[0]  # Punto mínimo (esquina inferior izquierda)
        xmax, ymax = bounds[1]  # Punto máximo (esquina superior derecha)
        
        ax.add_patch(patches.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, 
                                       linewidth=2, edgecolor=colores[i], 
                                       facecolor=colores[i], alpha=0.4, 
                                       label=f'Subregión {i+1}'))

    ax.set_xlim(-1, 5)
    ax.set_ylim(-1, 5)
    ax.set_aspect('equal')
    ax.set_title(titulo)
    ax.grid(True, linestyle=':', alpha=0.7)
    ax.legend(loc='upper right')

def correr_test_integracion():
    fabrica = Geometry2d()
    motor_predicados = Predicates2d()

    # 1. Definimos el Politopo Principal (Un cuadrado de 4x4)
    main_polytope = crear_caja(0.0, 4.0, 0.0, 4.0)

    # 2. ESCENARIO A: Cobertura Total
    # Partimos el 4x4 en dos mitades verticales exactas
    sub_ok_1 = crear_caja(0.0, 2.0, 0.0, 4.0)
    sub_ok_2 = crear_caja(2.0, 4.0, 0.0, 4.0)
    
    mapa_ok: PolytopeMap = [
        extraer_semiespacios(sub_ok_1, fabrica),
        extraer_semiespacios(sub_ok_2, fabrica)
    ]

    # 3. ESCENARIO B: Cobertura Fallida (Dejamos un hueco a la derecha)
    sub_fail_1 = crear_caja(0.0, 2.0, 0.0, 4.0)
    sub_fail_2 = crear_caja(2.0, 3.0, 0.0, 4.0) # Llega hasta x=3, deja un hueco de 3 a 4
    
    mapa_fail: PolytopeMap = [
        extraer_semiespacios(sub_fail_1, fabrica),
        extraer_semiespacios(sub_fail_2, fabrica)
    ]

    # 4. Ejecutamos el SCIChecker para ambos casos
    # Nota: Si tu clase PolytopeTriangulator todavía no está terminada, 
    # la ejecución va a frenar ahí.
    print("--- INICIANDO TEST DE INTEGRACIÓN ---")
    
    checker_ok = SCIChecker(fabrica, motor_predicados, main_polytope, mapa_ok)
    resultado_ok = checker_ok.sci_check()
    print(f"Escenario A (Cobertura Total) -> Esperado: True | Obtenido: {resultado_ok}")

    checker_fail = SCIChecker(fabrica, motor_predicados, main_polytope, mapa_fail)
    resultado_fail = checker_fail.sci_check()
    print(f"Escenario B (Con Hueco)       -> Esperado: False | Obtenido: {resultado_fail}")

    # 5. Graficamos ambos escenarios lado a lado
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    graficar_escenario(main_polytope, [sub_ok_1, sub_ok_2], f"Escenario A (Cubre todo)\nResultado SCI: {resultado_ok}", ax1)
    graficar_escenario(main_polytope, [sub_fail_1, sub_fail_2], f"Escenario B (Deja hueco)\nResultado SCI: {resultado_fail}", ax2)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    correr_test_integracion()