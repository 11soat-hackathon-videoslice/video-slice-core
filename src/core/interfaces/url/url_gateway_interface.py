from abc import ABC, abstractmethod

from core.domain.url import Url


class UrlGatewayInterface(ABC):

    @abstractmethod
    def generate_download_presigned_url(self, url: Url) -> Url:
        pass

    @abstractmethod
    def generate_upload_presigned_url(self, url: Url) -> Url:
        pass