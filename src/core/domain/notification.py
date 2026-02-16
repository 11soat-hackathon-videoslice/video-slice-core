from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from core.domain.vdsc_metadata import VdscMetadata
from core.enums.email_template_enum import EmailTemplateEnum
from core.enums.notification_channels_enum import NotificationChannelsEnum

if TYPE_CHECKING:
    from core.dtos.notification_dto import NotificationDto, EmailPayloadDto, WebPayloadDto

@dataclass(frozen=True)
class EmailPayload:
    user_id: str
    template: EmailTemplateEnum

    @staticmethod
    def from_dto(dto: 'EmailPayloadDto') -> 'EmailPayload':
        return EmailPayload(
            user_id=dto.user_id,
            template=dto.template
        )

@dataclass(frozen=True)
class WebPayload:
    user_id: str
    message: str
    timestamp: datetime

    @staticmethod
    def from_dto(dto: 'WebPayloadDto') -> 'WebPayload':
        return WebPayload(
            user_id=dto.user_id,
            message=dto.message,
            timestamp=dto.timestamp
        )

# Representa o conjunto de conteúdos possíveis
@dataclass(frozen=True)
class NotificationContent:
    email: Optional[EmailPayload] = None
    web: Optional[WebPayload] = None

@dataclass(frozen=True)
class Notification:
    id: UUID
    channels: list[NotificationChannelsEnum]
    metadata: VdscMetadata
    content: list[NotificationContent]

    def __post_init__(self):
        self._validate_channels()

    def _validate_channels(self):
        # Validação semântica: se o canal exige um payload, ele deve estar presente
        if NotificationChannelsEnum.EMAIL in self.channels and not any(c.email for c in self.content):
            raise ValueError("Canal EMAIL requer EmailPayload")
        if NotificationChannelsEnum.WEB in self.channels and not any(c.web for c in self.content):
            raise ValueError("Canal WEB requer WebPayload")

    @staticmethod
    def from_dto(dto: 'NotificationDto') -> 'Notification':
        return Notification(
            id=UUID(dto.id),
            channels=dto.channels,
            metadata=VdscMetadata(dto=dto.metadata),
            content=[NotificationContent(
                email=EmailPayload.from_dto(content.email) if content.email else None,
                web=WebPayload.from_dto(content.web) if content.web else None
            ) for content in dto.content]
        )

