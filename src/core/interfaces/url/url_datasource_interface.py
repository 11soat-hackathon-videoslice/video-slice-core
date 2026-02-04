from abc import ABC, abstractmethod

from core.dtos.url_dto import UrlRequestDto, UrlResponseDto


class UrlDataSourceInterface(ABC):

    @abstractmethod
    def generate_download_presigned_url(self, url: UrlRequestDto) -> UrlResponseDto:
        pass

    @abstractmethod
    def generate_upload_presigned_url(self, url: UrlRequestDto) -> UrlResponseDto:
        pass