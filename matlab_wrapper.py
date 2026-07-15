import numpy as np
# from tu_modulo import SCIChecker, Geometry, Predicates, extraer_semiespacios
from sci import SCIChecker
from geometry.geometry_2d import Geometry2d
from coverage_checker.predicates_2d import Predicates2d
import polytope as pc
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt

def guardar_plot_debug(polytope_verts_raw, subregions_verts_raw, filename="/home/tomi/Escritorio/Pasantía/SCI-check/debug_geometria_python.png"):
    fig, ax = plt.subplots(figsize=(8, 8))
    colores = ['red', 'blue', 'green', 'orange', 'purple', 'cyan', 'magenta', 'yellow']
    
    # Dibujar las subregiones ORDENADAS
    for i, sub_raw in enumerate(subregions_verts_raw):
        if len(sub_raw) < 3:
            continue
            
        sub_arr = np.array(sub_raw, dtype=float)
        
        # APLICAMOS CONVEX HULL PARA EL DIBUJO
        try:
            hull = ConvexHull(sub_arr)
            # Ordenamos los vértices para que formen el polígono perimetral
            sub_arr_ordenado = sub_arr[hull.vertices]
        except Exception:
            print("Excepción")
            sub_arr_ordenado = sub_arr
            
        sub_cerrado = np.vstack((sub_arr_ordenado, sub_arr_ordenado[0]))
        color_actual = colores[i % len(colores)]
        
        ax.plot(sub_cerrado[:, 0], sub_cerrado[:, 1], color=color_actual, linewidth=2, label=f'Subregión {i+1}')
        ax.fill(sub_cerrado[:, 0], sub_cerrado[:, 1], color=color_actual, alpha=0.3)
        ax.scatter(sub_arr[:, 0], sub_arr[:, 1], color=color_actual, s=30, zorder=5)

    # Dibujar P
    P_arr = np.array(polytope_verts_raw, dtype=float)
    try:
        hull_P = ConvexHull(P_arr)
        for simplex in hull_P.simplices:
            ax.plot(P_arr[simplex, 0], P_arr[simplex, 1], 'k-', linewidth=3, zorder=10)
    except:
        pass
    
    ax.set_aspect('equal', 'box')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()

def checking_sci(polytope_verts_raw, subregions_verts_raw, dimension): # tipar esto y emprolijar
    """
    Recibe listas crudas desde MATLAB, arma la geometría y corre el SCIChecker.
    """

    dimDict = {2: (Geometry2d, Predicates2d)} # diccionario para la dimensión. MOVER A COMMON.

    print(">>> [PYTHON] Entrando al wrapper. Recibiendo datos...", flush=True)
    guardar_plot_debug(polytope_verts_raw, subregions_verts_raw)
    print(">>> [PYTHON] Grafico guardado", flush=True)
    # 1. Convertir los datos crudos a arrays de numpy
    P_verts = np.round(np.array(polytope_verts_raw, dtype=float)) # vértices del politopo
    
    # 2. Inicializar tu motor geométrico
    geomClass, predClass = dimDict[dimension]
    geom = geomClass()
    preds = predClass()
    
    # 3. Armar el politopo principal
    P = pc.qhull(P_verts) # se crea el politopo
    
    # 4. Armar las subregiones
    subs_c3 = []
    for sub_raw in subregions_verts_raw:
        # sub_raw es una lista de coordenadas [[x1, y1], [x2, y2], ...]
        n_verts = len(sub_raw)
        
        # Filtro de seguridad: un polígono necesita al menos 3 vértices
        if n_verts < 3:
            continue 

        # 1. Convertimos la subregión a un array de NumPy
        puntos_desordenados = np.array(sub_raw, dtype=float)
        
        # 2. LA MAGIA: Calculamos el Hull. 
        # hull.vertices contiene los índices en sentido ANTIHORARIO perfecto.
        hull = ConvexHull(puntos_desordenados)
        puntos_ordenados = puntos_desordenados[hull.vertices]
        #puntos_ordenados = puntos_ordenados[::-1]
        
        n_ordenados = len(puntos_ordenados)
        sub_halfspaces = []
        
        # Iteramos para armar los bordes (v1, v2)
        for i in range(n_ordenados):
            v1 = puntos_ordenados[i]
            # El módulo asegura que el último vértice se una con el primero (índice 0)
            v2 = puntos_ordenados[(i + 1) % n_ordenados]
            
            p1 = geom.create_point(v1)
            p2 = geom.create_point(v2)
            hs = geom.create_halfspace((p1, p2))
            
            sub_halfspaces.append(hs)
            
        # Agregamos la lista de semiespacios terminada a la lista maestra
        subs_c3.append(sub_halfspaces)

    # 5. Instanciar el checker y correrlo
    checker = SCIChecker(geom, preds, P, subs_c3)
    resultado = checker.sci_check()
    
    # Retornamos un booleano estándar que MATLAB entiende perfecto
    return bool(resultado)