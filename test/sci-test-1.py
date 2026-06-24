import sys
import os

# 1. Calculamos la ruta absoluta a la carpeta raíz del proyecto (subiendo un nivel '..')
ruta_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 2. Inyectamos esa ruta en el radar de búsqueda de Python
sys.path.insert(0, ruta_raiz)

from geometry.geometry_2d import Geometry2d
from coverage_checker.predicates_2d import Predicates2d
from common.enums import OrientResult
# Asegurate de importar tu clase CoverageChecker/EnvelopeChecker acá
from coverage_checker.coverage_checker import CoverageChecker 

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def correr_prueba_c1():
    # 1. Inicializamos nuestras dependencias
    geometria = Geometry2d()
    predicados = Predicates2d()
    checker = CoverageChecker(geometry=geometria, predicates=predicados) 

    # 2. fabricamos los 3 vértices de prueba
    v1 = geometria.create_point((1.0, 1.0)) # Esperado: IN (Adentro de R1)
    v2 = geometria.create_point((3.0, 1.0)) # Esperado: IN (Adentro de R2)
    v3 = geometria.create_point((1.0, 4.0)) # Esperado: OUT (Afuera de todo)

    # 3. fabricamos las caras (Halfspaces) de la Subregión 1 [x: 0 a 2, y: 0 a 2]
    # Puntos ordenados en CCW: (0,0) -> (2,0) -> (2,2) -> (0,2)
    p1_bl = geometria.create_point((0.0, 0.0)) # Bottom-Left
    p1_br = geometria.create_point((2.0, 0.0)) # Bottom-Right
    p1_tr = geometria.create_point((2.0, 2.0)) # Top-Right
    p1_tl = geometria.create_point((0.0, 2.0)) # Top-Left

    # Creamos las aristas uniendo los puntos en sentido antihorario
    r1_bot   = geometria.create_halfspace((p1_bl, p1_br))
    r1_right = geometria.create_halfspace((p1_br, p1_tr))
    r1_top   = geometria.create_halfspace((p1_tr, p1_tl))
    r1_left  = geometria.create_halfspace((p1_tl, p1_bl))

    # 4. fabricamos las caras de la Subregión 2 [x: 2 a 4, y: 0 a 2]
    # Puntos ordenados en CCW: (2,0) -> (4,0) -> (4,2) -> (2,2)
    p2_bl = geometria.create_point((2.0, 0.0))
    p2_br = geometria.create_point((4.0, 0.0))
    p2_tr = geometria.create_point((4.0, 2.0))
    p2_tl = geometria.create_point((2.0, 2.0))

    r2_bot   = geometria.create_halfspace((p2_bl, p2_br))
    r2_right = geometria.create_halfspace((p2_br, p2_tr))
    r2_top   = geometria.create_halfspace((p2_tr, p2_tl))
    r2_left  = geometria.create_halfspace((p2_tl, p2_bl))

    # 5. Armamos la lista de sets que simula tu PolytopeMap (usando IDs enteros o lista simple)
    polytope_set_mock = [
        {r1_top, r1_bot, r1_right, r1_left},
        {r2_top, r2_bot, r2_right, r2_left}
    ]

    # 6. Ejecutamos el método
    print("--- INICIANDO TEST CONDICIÓN C1 ---")
    
    res_v1 = checker.point_out(v1, polytope_set_mock)
    print(f"Vértice 1 (1,1)  -> Esperado: IN  | Obtenido: {res_v1}")
    
    res_v2 = checker.point_out(v2, polytope_set_mock)
    print(f"Vértice 2 (3,1)  -> Esperado: IN  | Obtenido: {res_v2}")
    
    res_v3 = checker.point_out(v3, polytope_set_mock)
    print(f"Vértice 3 (1,4)  -> Esperado: OUT | Obtenido: {res_v3}")

def graficar_escenario_test():
    # Creamos la figura y los ejes
    fig, ax = plt.subplots(figsize=(8, 8))

    # 1. Dibujamos la Subregión 1 (Cuadrado de 0 a 2)
    r1 = patches.Rectangle((0, 0), 2, 2, linewidth=2, edgecolor='blue', 
                           facecolor='lightblue', alpha=0.4, label='Subregión 1')
    ax.add_patch(r1)

    # 2. Dibujamos la Subregión 2 (Cuadrado de 2 a 4)
    r2 = patches.Rectangle((2, 0), 2, 2, linewidth=2, edgecolor='green', 
                           facecolor='lightgreen', alpha=0.4, label='Subregión 2')
    ax.add_patch(r2)

    # 3. Coordenadas de los vértices que armamos
    # V1(1,1), V2(3,1), V3(1,4)
    x_coords = [1.0, 3.0, 1.0]
    y_coords = [1.0, 1.0, 4.0]
    nombres = ['V1 (Esperado: IN)', 'V2 (Esperado: IN)', 'V3 (Esperado: OUT)']
    colores = ['blue', 'green', 'red']

    # Punteamos los vértices
    for x, y, nombre, color in zip(x_coords, y_coords, nombres, colores):
        ax.plot(x, y, marker='o', markersize=8, color=color)
        ax.text(x + 0.1, y + 0.1, nombre, fontsize=10, weight='bold')

    # 4. Dibujamos el triángulo que forman (con línea punteada)
    triangulo = patches.Polygon(xy=list(zip(x_coords, y_coords)), closed=True, 
                                fill=False, edgecolor='black', linestyle='--', 
                                linewidth=1.5, label='Triángulo de la malla')
    ax.add_patch(triangulo)

    # 5. Configuramos la grilla y la vista
    ax.set_xlim(-1, 5)
    ax.set_ylim(-1, 5)
    ax.set_aspect('equal') # Fundamental para que los cuadrados no se vean rectangulares
    ax.set_title('Visualización del Test - Condición C1', fontsize=14)
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')
    ax.grid(True, linestyle=':', alpha=0.7)
    ax.legend(loc='upper right')

    # Mostramos la ventana emergente
    plt.show()

if __name__ == "__main__":
    correr_prueba_c1()
    graficar_escenario_test()