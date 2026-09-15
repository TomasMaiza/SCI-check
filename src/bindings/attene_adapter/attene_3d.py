from geometry.structs_3d import *
from .attene import AtteneAdapter
from .. import pyattene

class AtteneAdapter3D(AtteneAdapter):
  # clase de adaptador 2d para la librería de implicit predicates

  def create_explicit_point(self, point: Point3D): 
    # crea un punto explícito
    pass

  def create_explicit_points_from_halfspace(self, hs: Halfspace3D): 
    # retorna los puntos explícitos que definen un semiespacio
    pass

  def create_implicit_point_lpi(self, 
                                p1: Point3D, 
                                p2: Point3D, 
                                plane: Halfspace3D): 
    # crea un punto implícito LPI (intersección de p1p2 con plane)
    pass

  def create_implicit_point_lpi(self, 
                                p1: Halfspace3D, 
                                p2: Halfspace3D, 
                                p3: Halfspace3D): 
    # crea un punto implícito TPI (intersección de los tres planos)
    pass