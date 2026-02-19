from abc import ABC, abstractmethod

class ImageProvider(ABC):
    @abstractmethod
    def search(self, q: str, limit: int = 24):
        raise NotImplementedError
