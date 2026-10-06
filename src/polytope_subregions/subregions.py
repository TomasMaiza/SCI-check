import numpy as np
import numpy.typing as npt
from scipy.spatial import ConvexHull
from .subregionsStrategy import SubregionsStrategy
from affine_system import *
from geometry import Halfspace, AbstractGeometry, Polytope
from .approximations import Euler, Taylor
from affine_system import SwitchedAffineSystem, AffineMode
from .matrices import partition_matrices, partition_matrices_bound

class Subregions(SubregionsStrategy):
  def __init__(self, dimension: int):
    self._approxMethod = Taylor
    self._dimension = dimension
  
  def get_subregion(self, 
                    subsystem: AffineMode, 
                    polytope: Polytope) -> Polytope:
    # obtiene la subregión para un modo particular
    approx = self._approxMethod(subsystem, polytope, scaling=1, order=4)
    r = 0 # r_0
    errorSeq = approx.error_sequence(self._h, self._K)
    phi = approx.get_matrix(self._h) # matriz de la aproximación
    dim = phi.shape[0]
    phi_k = np.eye(dim, dtype=np.float64) # matriz de la aproximación para el paso k
    Hplus, Hminus = partition_matrices(polytope, subsystem, self._h)
    subregionH = [] # apilamos las matrices de las inecuaciones
    subregionc = []
    for k in range(0, self._K + 1):
      r = errorSeq[k]
      midr = approx.error_bound(r, self._h/2)
      # calcular H una sola vez fuera del for
      c = partition_matrices_bound(polytope, r, midr) 
      if k > 0:
        subregionH.append(Hminus @ phi_k)
        subregionc.append(c)
      if k < self._K:
        subregionH.append(Hplus @ phi_k)
        subregionc.append(c)
      phi_k = phi @ phi_k
    matrixH = np.vstack(subregionH)
    matrixc = np.vstack(subregionc)
    # obtengo A y b separando la última columna de matrixH y me queda que Ax <= c - b
    matrixA, matrixb = np.hsplit(matrixH, [dim - 1]) # obtiene A y b separando la últ col de H
    matrixb = matrixc - matrixb
    subregionPolytope = type(polytope)(intDim = self._dimension, ambDim = self._dimension, A = matrixA, b = matrixb)
    #subregionPolytope.reduce()
    return subregionPolytope

  def get_subregions(self, 
                     sas: SwitchedAffineSystem, 
                     polytope: Polytope, 
                     dwellTime: float, 
                     K: int) -> list[Polytope]:
    # recibe un politopo, el sistema y los parámetros para devolver la lista de subregiones
    h = dwellTime/K
    self._K = K
    self._h = h
    modes = sas.get_all_modes()
    polytopeMap = [] # inicializo el mapa de politopos para cada modo
    for i in modes:
      subsystem = sas.get_subsystem(i)
      subregionPolytope = self.get_subregion(subsystem, polytope)
      #if len(halfspaces) != 0:
      polytopeMap.append(subregionPolytope)
    return polytopeMap

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import ConvexHull
import polytope as pc
import numpy as np

def plot_polytope(A, b, k, original_polytope):
    try:
        # 1. Vértices de la subregión dinámica
        try:
            poly_sub = pc.Polytope(A, b)
            V_sub = pc.extreme(poly_sub)
        except Exception:
            V_sub = None
            
        # 2. Vértices del politopo original
        V_orig = np.array(original_polytope.get_vertices(), dtype=float)
        
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # 3. JAULA ROJA: Trazamos las aristas con ax.plot (evita el bug de la caja negra)
        if V_orig is not None and len(V_orig) >= 4:
            hull_orig = ConvexHull(V_orig)
            for simplex in hull_orig.simplices:
                # Cerramos el triángulo agregando el primer punto al final
                s = np.append(simplex, simplex[0])
                ax.plot(V_orig[s, 0], V_orig[s, 1], V_orig[s, 2], color='red', linewidth=1.2, alpha=0.8)
                
        # 4. VOLUMEN CYAN: La subregión
        if V_sub is not None and len(V_sub) >= 4:
            hull_sub = ConvexHull(V_sub)
            faces_sub = [V_sub[simplex] for simplex in hull_sub.simplices]
            poly3d_sub = Poly3DCollection(faces_sub, facecolors='cyan', edgecolors='blue', linewidths=1.5, alpha=0.4)
            ax.add_collection3d(poly3d_sub)
        else:
            # Si SVD orientó mal el normal, caerá directamente aquí en k=0
            print(f"k={k}: La subregión cortó todo el volumen y quedó VACÍA.")
            
        # 5. Límites dinámicos
        if V_sub is not None and len(V_sub) > 0 and V_orig is not None and len(V_orig) > 0:
            all_V = np.vstack((V_orig, V_sub))
        elif V_orig is not None and len(V_orig) > 0:
            all_V = V_orig
        elif V_sub is not None and len(V_sub) > 0:
            all_V = V_sub
        else:
            all_V = np.array([[-1,-1,-1], [1,1,1]])
            
        ax.set_xlim([all_V[:,0].min() - 0.05, all_V[:,0].max() + 0.05])
        ax.set_ylim([all_V[:,1].min() - 0.05, all_V[:,1].max() + 0.05])
        ax.set_zlim([all_V[:,2].min() - 0.05, all_V[:,2].max() + 0.05])
        
        ax.set_title(f"Cobertura en k = {k}\nLíneas Rojas: Original | Volumen Cyan: Subregión")
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        
        # 6. Control interactivo a prueba de clicks
        plt.show(block=False) 
        print(f"Mostrando k={k}. Usá el mouse para rotar. Presioná CUALQUIER TECLA para avanzar...")
        
        while True:
            if plt.waitforbuttonpress():
                break
                
        plt.close(fig) 
        
    except Exception as e:
        print(f"No se pudo graficar en 3D para k={k}. Motivo general: {e}")

