from core.domain.notification import Notification
from core.dtos.notification_dto import NotificationDto
from core.enums.notification_channels_enum import NotificationChannelsEnum
from core.interfaces.notification.notication_interfaces import NotificationGatewayInterface


class SendNotificationEmailUseCase:

    def execute(self, notification_dto: NotificationDto, gateway: NotificationGatewayInterface) -> None:
        if NotificationChannelsEnum.EMAIL not in notification_dto.channels:
            raise ValueError("Canal inválido para este caso de uso. Canal esperado: EMAIL")

        notification = Notification.from_dto(notification_dto)
        gateway.send(notification)

