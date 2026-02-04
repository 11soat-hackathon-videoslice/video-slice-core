from abc import ABC, abstractmethod

from core.dtos.url_dto import UrlRequestDto

class UrlControllerInterface(ABC):

    @abstractmethod
    def generate_presigned_url(self, request: UrlRequestDto) -> dict:
        pass
