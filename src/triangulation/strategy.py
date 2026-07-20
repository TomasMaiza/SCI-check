from abc import ABC, abstractmethod
import numpy as np

class TriangulationAlgorithm(ABC):
    @abstractmethod
    def triangulate(self, vertices: np.ndarray) -> list[np.ndarray]:
        # Recibe un array de vértices y devuelve una lista de arreglos que representan triángulos
        pass