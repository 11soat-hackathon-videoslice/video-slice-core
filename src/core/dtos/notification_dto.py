import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from core.enums.email_template_enum import EmailTemplateEnum
from core.enums.notification_channels_enum import NotificationChannelsEnum
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO
from core.domain.notification import Notification

@dataclass(frozen=True)
class EmailPayloadDto:
    user_id: str
    template: EmailTemplateEnum

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "template": self.template.name
        }

    def to_json(self) -> str:
        """Converte o objeto para formato JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def from_dict(self):
        return EmailPayloadDto(
            user_id=self.user_id,
            template=EmailTemplateEnum[self.template]
        )

@dataclass(frozen=True)
class WebPayloadDto:
    user_id: str
    message: str
    timestamp: datetime
    is_read: bool

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "is_read": self.is_read
        }

    def to_json(self) -> str:
        """Converte o objeto para formato JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def from_dict(self):
        return WebPayloadDto(
            user_id=self.user_id,
            message=self.message,
            timestamp=datetime.now(),
            is_read=self.is_read
        )

@dataclass(frozen=True)
class NotificationContentDto:
    email: Optional[EmailPayloadDto] = None
    web: Optional[WebPayloadDto] = None

    def to_dict(self) -> dict:
        return {
            "email": self.email.to_dict() if self.email else None,
            "web": self.web.to_dict() if self.web else None
        }

    def to_json(self) -> str:
        """Converte o objeto para formato JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def from_dict(self):
        return NotificationContentDto(
            email=EmailPayloadDto.from_dict(self.email) if self.email else None,
            web=WebPayloadDto.from_dict(self.web) if self.web else None
        )


@dataclass(frozen=True)
class NotificationDto:
    id: str
    channels: list[NotificationChannelsEnum]
    metadata: VdscMetadataDTO
    content: list[NotificationContentDto]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "channels": [channel.name for channel in self.channels],
            "metadata": self.metadata.to_dict(),
            "content": [content.to_dict() for content in self.content]
        }

    def to_json(self) -> str:
        """Converte o objeto para formato JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def from_dict(self):
        return NotificationDto(
            id=self.id,
            channels=[NotificationChannelsEnum[channel] for channel in self.channels],
            metadata=VdscMetadataDto.from_dict(self.metadata),
            content=[NotificationContentDto.from_dict(content) for content in self.content]
        )

    def __post_init(self):
        self._validate_channels()

    def _validate_channels(self):
        # Validação semântica: se o canal exige um payload, ele deve estar presente
        if NotificationChannelsEnum.EMAIL in self.channels and not any(content.email for content in self.content):
            raise ValueError("Canal EMAIL requer EmailPayload")
        if NotificationChannelsEnum.WEB in self.channels and not any(content.web for content in self.content):
            raise ValueError("Canal WEB requer WebPayload")

    @staticmethod
    def from_domain(notification: 'Notification') -> 'NotificationDto':
        # Converter conteúdos do domínio para DTOs
        content_dtos = []
        for content in notification.content:
            email_dto = None
            web_dto = None

            if content.email:
                email_dto = EmailPayloadDto(
                    user_id=content.email.user_id,
                    template=content.email.template
                )

            if content.web:
                web_dto = WebPayloadDto(
                    user_id=content.web.user_id,
                    message=content.web.message,
                    timestamp=content.web.timestamp,
                    is_read=content.web.is_read
                )

            content_dtos.append(NotificationContentDto(email=email_dto, web=web_dto))

        # Converter VdscMetadata domain para VdscMetadataDTO usando o método from_domain
        metadata_dto = VdscMetadataDTO.from_domain(notification.metadata)

        return NotificationDto(
            id=str(notification.id),
            channels=notification.channels,
            metadata=metadata_dto,
            content=content_dtos
        )
