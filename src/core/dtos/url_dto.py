from typing import Optional, Dict


class UrlRequestDto:
    file_name: str
    action: str

    def __init__(self, file_name: str, action: str):
        self.file_name = file_name
        self.action = action


    def to_dict(self) -> dict:
        return {
            "file_name": self.file_name,
            "action": self.action
        }
    @classmethod
    def from_dict(cls, data: dict) -> 'UrlRequestDto':
        return cls(
            file_name=data['file_name'],
            action=data['action']
        )
    def add_new_fields(self, fields: dict):
        setattr(self, 'fields', fields)

    @classmethod
    def from_domain(cls, url: 'Url') -> 'UrlRequestDto':
        return cls(file_name=url.file_name,action=url.action)

class UrlResponseDto:
    url_endpoint: str
    file_name: str
    action: str
    method: str
    fields: Optional[Dict[str, str]] = None

    def __init__(self, url_endpoint: str, file_name: str, action: str, method: str, fields: Optional[Dict[str, str]] = None):
        self.url_endpoint = url_endpoint
        self.file_name = file_name
        self.action = action
        self.method = method
        self.fields = fields

    def to_dict(self) -> dict:
        return {
            "url_endpoint": self.url_endpoint,
            "file_name": self.file_name,
            "action": self.action,
            "method": self.method,
            "fields": self.fields
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'UrlResponseDto':
        return cls(
            url_endpoint=data['url_endpoint'],
            file_name=data['file_name'],
            action=data['action'],
            method=data['method'],
            fields=data.get('fields')
        )