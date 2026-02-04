from core.domain.url import Url
from core.dtos.url_dto import UrlResponseDto

class UrlPresenter:

    def return_generate_presigned_url(self, url: Url) -> UrlResponseDto:
        return UrlResponseDto(
            url_endpoint=url.url_endpoint,
            file_name=url.file_name,
            action=url.action,
            method=url.method,
            fields=url.fields
        )

