from abc import ABC, abstractmethod

from core.domain import Url
from core.dtos import UrlRequestDto, UrlResponseDto


class UrlGatewayInterface(ABC):

    @abstractmethod
    def generate_download_presigned_url(self, url: Url) -> Url:
        pass

    @abstractmethod
    def generate_upload_presigned_url(self, url: Url) -> Url:
        pass


class UrlDataSourceInterface(ABC):

    @abstractmethod
    def generate_download_presigned_url(self, url: UrlRequestDto) -> UrlResponseDto:
        pass

    @abstractmethod
    def generate_upload_presigned_url(self, url: UrlRequestDto) -> UrlResponseDto:
        pass


class UrlControllerInterface(ABC):

    @abstractmethod
    def generate_presigned_url(self, request: UrlRequestDto) -> dict:
        pass
