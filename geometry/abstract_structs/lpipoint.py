from abc import ABC, abstractmethod
from .point import AbstractPoint
import numpy as np

class AbstractLPIPoint(ABC):
  # representación de un punto lpi en un espacio n-dimensional
  @abstractmethod
  def get_edge(self) -> tuple[AbstractPoint, ...]: # permite obtener la arista
    pass