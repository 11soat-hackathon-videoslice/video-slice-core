from core.adapters.notification.notification_gateway import NotificationGateway
from core.applications.notification.send_notification_use_case_factory import SendNotificationUseCaseFactory
from core.applications.notification.send_notification_email_use_case import SendNotificationEmailUseCase
from core.applications.notification.send_notification_web_use_case import SendNotificationWebUseCase
from core.dtos.notification_dto import NotificationDto
from core.enums.notification_channels_enum import NotificationChannelsEnum
from core.interfaces.notification.notication_interfaces import NotificationControllerInterface, \
    NotificationDatasourceInterface


class NotificationController(NotificationControllerInterface):

    def __init__(self, datasource: NotificationDatasourceInterface):
        self.datasource = datasource
        self.factory_use_case = SendNotificationUseCaseFactory(
            SendNotificationEmailUseCase(),
            SendNotificationWebUseCase()
        )

    def send(self, notification: NotificationDto, channel: NotificationChannelsEnum) -> None:
        gateway = NotificationGateway(self.datasource)
        use_case = self.factory_use_case.get_use_case(channel)
        use_case.execute(notification, gateway)


