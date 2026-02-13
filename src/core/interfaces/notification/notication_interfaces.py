from abc import ABC, abstractmethod

from core.domain.notification import Notification
from core.dtos.notification_dto import NotificationDto
from core.enums import NotificationChannelsEnum


class NotificationControllerInterface(ABC):
    @abstractmethod
    def send(self, notification: 'NotificationDto', channel: NotificationChannelsEnum) -> None:
        pass

class NotificationGatewayInterface(ABC):
    @abstractmethod
    def send(self, notification: 'Notification') -> None:
        pass
class NotificationDatasourceInterface(ABC):
    @abstractmethod
    def send(self, notification: 'NotificationDto') -> None:
        pass
class NotificationUseCaseInterface(ABC):
    @abstractmethod
    def execute(self, dto: 'NotificationDto') -> None:
        pass
