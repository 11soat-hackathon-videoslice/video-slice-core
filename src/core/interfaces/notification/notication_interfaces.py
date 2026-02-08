from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.domain.notification import Notification
    from core.dtos.notification_dto import NotificationDto
class NotificationControllerInterface(ABC):
    @abstractmethod
    def send(self, notification: 'NotificationDto') -> None:
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
