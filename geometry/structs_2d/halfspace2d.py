from geometry.abstract_structs.halfspace import AbstractHalfspace
from .point2d import Point2D
import numpy as np
from dataclasses import dataclass

@dataclass(frozen=True)
class Halfspace2D(AbstractHalfspace):
  # representación de un semiespacio en 2D
  p1: Point2D
  p2: Point2D

  def get_points(self) -> tuple[Point2D, Point2D]: 
    return self.p1, self.p2