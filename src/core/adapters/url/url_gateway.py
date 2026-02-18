from core.domain.url import Url
from core.dtos.url_dto import UrlRequestDto
from core.interfaces import UrlGatewayInterface, UrlDataSourceInterface


class UrlGateway(UrlGatewayInterface):

    def __init__(self, datasource: UrlDataSourceInterface):
        self.datasource = datasource

    def generate_download_presigned_url(self, url: Url) -> Url:
        request_dto = UrlRequestDto.from_domain(url)
        response_dto = self.datasource.generate_download_presigned_url(request_dto)
        return Url.from_response(response_dto)

    def generate_upload_presigned_url(self, url: Url) -> Url:
        request_dto = UrlRequestDto.from_domain(url)
        response_dto = self.datasource.generate_upload_presigned_url(request_dto)
        return Url.from_response(response_dto)

