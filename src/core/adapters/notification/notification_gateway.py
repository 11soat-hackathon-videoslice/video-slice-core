from core.domain.notification import Notification
from core.dtos.notification_dto import NotificationDto
from core.interfaces.notification.notication_interfaces import (NotificationGatewayInterface,
                                                                NotificationDatasourceInterface)


class NotificationGateway(NotificationGatewayInterface):

    def __init__(self, datasource: NotificationDatasourceInterface):
        self.datasource = datasource

    def send(self, notification: Notification) -> None:
        notification_dto = NotificationDto.from_domain(notification)
        self.datasource.send(notification_dto)

