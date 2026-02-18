from typing import Optional, Dict


class Url:
    url_endpoint: str
    file_name: str
    action: str
    method: str
    fields: Optional[Dict[str, str]] = None

    def __init__(
            self,
            file_name: str,
            action: str,
            method: Optional[str] = None,
            url_endpoint: Optional[str] = None,
            fields: Optional[Dict[str, str]] = None
    ):
        self.file_name = file_name
        self.action = action
        self.method = method
        self.url_endpoint = url_endpoint
        self.fields = fields

    @classmethod
    def from_request(cls, dto: 'UrlRequestDto') -> 'Url':
        return cls(
            file_name=dto.file_name,
            action=dto.action
        )

    @classmethod
    def from_response(cls, dto: 'UrlResponseDto') -> 'Url':
        return cls(
            url_endpoint=dto.url_endpoint,
            file_name=dto.file_name,
            action=dto.action,
            method=dto.method,
            fields=dto.fields
        )

    def to_dict(self) -> dict:
        return {
            "url_endpoint": self.url_endpoint,
            "file_name": self.file_name,
            "action": self.action,
            "method": self.method,
            "fields": self.fields
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Url':
        return cls(
            url_endpoint=data.get('url_endpoint'),
            file_name=data['file_name'],
            action=data['action'],
            method=data['method'],
            fields=data.get('fields')
        )

    def update_presigned_data(self, url: str, fields: Optional[Dict] = None):
        self.url_endpoint = url
        self.fields = fields


