from core.domain.url import Url

class UrlPresenter:

    def return_generate_presigned_url(self, url: Url) -> dict:
        return {
            "url": url.url_endpoint,
            "FileName": url.file_name,
            "expiresIn": url.fields["expireIn"],
            "s3Key": url.fields["s3Key"],
            "action": url.action,
            "method": url.method
        }
