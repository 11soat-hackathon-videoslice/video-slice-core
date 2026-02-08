from core.enums.notification_channels_enum import NotificationChannelsEnum
from core.applications.notification.send_notification_email_use_case import SendNotificationEmailUseCase
from core.applications.notification.send_notification_web_use_case import SendNotificationWebUseCase


class SendNotificationUseCaseFactory:

    def __init__(self, email_use_case: SendNotificationEmailUseCase, web_use_case: SendNotificationWebUseCase):
        self._use_cases = {
            NotificationChannelsEnum.EMAIL: email_use_case,
            NotificationChannelsEnum.WEB: web_use_case
        }

    def get_use_case(self, channel: NotificationChannelsEnum):
        use_case = self._use_cases.get(channel)
        if not use_case:
            raise ValueError(f"Não encontrado caso de uso para o canal: {channel}")
        return use_case

