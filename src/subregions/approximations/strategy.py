from abc import ABC, abstractmethod
import numpy as np

class ApproximationStrategy(ABC):
  @abstractmethod
  def __init__(self):
    # Inicializa la función de aproximación y la función de error
    pass

  def apply_approx(self):
    # aplica la función de aproximación
    pass

  def get_error_bound(self):
    # calcula el error de la aproximación
    pass