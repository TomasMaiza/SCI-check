from geometry.abstract_structs.lpipoint import AbstractLPIPoint
from .point2d import Point2D
from .halfspace2d import Halfspace2D
import numpy as np
from dataclasses import dataclass

@dataclass(frozen=True)
class LPIPoint2D(AbstractLPIPoint):
  # representación de un punto lpi en 2 dimensiones
  x: Point2D # p1 y p2 definen un lado
  y: Point2D
  halfspace: Halfspace2D # define la cara

  @property
  def get_edge(self) -> tuple[Point2D, Point2D]:
        return (self.x, self.y)