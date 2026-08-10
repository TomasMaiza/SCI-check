from abc import ABC, abstractmethod
import numpy as np
from typing import Optional

class PolytopeImp:
  def __init__(self, 
                 vertices: Optional['tuple[AbstractPoint, ...]'], 
                 A: Optional['np.ndarray'], 
                 b: Optional['float']):
      pass