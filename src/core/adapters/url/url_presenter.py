from core.domain.url import Url

class UrlPresenter:

    def return_generate_presigned_url(self, url: Url) -> dict:
        return {
            "url_endpoint": url.url_endpoint,
            "file_name": url.file_name,
            "action": url.action,
            "method": url.method,
            "expiration": url.fields["expireIn"]
        }
