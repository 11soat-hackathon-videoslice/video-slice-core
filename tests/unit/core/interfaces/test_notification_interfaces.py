"""Testes para as interfaces de Notificação"""
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from core.domain.notification import Notification
from core.dtos.notification_dto import NotificationDto, NotificationContentDto, WebPayloadDto
from core.enums.notification_channels_enum import NotificationChannelsEnum
from core.interfaces.notification.notication_interfaces import (
    NotificationControllerInterface,
    NotificationGatewayInterface,
    NotificationDatasourceInterface,
    NotificationUseCaseInterface
)


@pytest.mark.unit
class TestNotificationControllerInterface:
    """Testes para NotificationControllerInterface"""

    def test_interface_is_abstract(self):
        """Testa que a interface é abstrata"""
        with pytest.raises(TypeError):
            NotificationControllerInterface()

    def test_interface_has_send_method(self):
        """Testa que a interface tem o método send"""
        assert hasattr(NotificationControllerInterface, 'send')

    def test_concrete_implementation_controller(self):
        """Testa implementação concreta do controller"""

        class ConcreteNotificationController(NotificationControllerInterface):
            def __init__(self):
                self.sent_notifications = []

            def send(self, notification: NotificationDto, channel: NotificationChannelsEnum) -> None:
                self.sent_notifications.append((notification, channel))

        controller = ConcreteNotificationController()

        notification = NotificationDto(
            id="test-id",
            channels=[NotificationChannelsEnum.WEB],
            content=[NotificationContentDto(
                web=WebPayloadDto(
                    message="Test",
                    timestamp=datetime.now(),
                    user_id="user"
                )
            )],
            metadata=MagicMock()
        )

        controller.send(notification, NotificationChannelsEnum.WEB)

        assert len(controller.sent_notifications) == 1
        assert controller.sent_notifications[0][0] == notification
        assert controller.sent_notifications[0][1] == NotificationChannelsEnum.WEB


@pytest.mark.unit
class TestNotificationGatewayInterface:
    """Testes para NotificationGatewayInterface"""

    def test_interface_is_abstract(self):
        """Testa que a interface é abstrata"""
        with pytest.raises(TypeError):
            NotificationGatewayInterface()

    def test_interface_has_send_method(self):
        """Testa que a interface tem o método send"""
        assert hasattr(NotificationGatewayInterface, 'send')

    def test_concrete_implementation_gateway(self):
        """Testa implementação concreta do gateway"""

        class ConcreteNotificationGateway(NotificationGatewayInterface):
            def __init__(self):
                self.notifications = []

            def send(self, notification: Notification) -> None:
                self.notifications.append(notification)

        gateway = ConcreteNotificationGateway()
        notification = MagicMock(spec=Notification)

        gateway.send(notification)

        assert len(gateway.notifications) == 1
        assert gateway.notifications[0] == notification


@pytest.mark.unit
class TestNotificationDatasourceInterface:
    """Testes para NotificationDatasourceInterface"""

    def test_interface_is_abstract(self):
        """Testa que a interface é abstrata"""
        with pytest.raises(TypeError):
            NotificationDatasourceInterface()

    def test_interface_has_send_method(self):
        """Testa que a interface tem o método send"""
        assert hasattr(NotificationDatasourceInterface, 'send')

    def test_concrete_implementation_datasource(self):
        """Testa implementação concreta do datasource"""

        class ConcreteNotificationDatasource(NotificationDatasourceInterface):
            def __init__(self):
                self.sent = False

            def send(self, notification: NotificationDto) -> None:
                self.sent = True

        datasource = ConcreteNotificationDatasource()
        notification = MagicMock(spec=NotificationDto)

        datasource.send(notification)

        assert datasource.sent is True


@pytest.mark.unit
class TestNotificationUseCaseInterface:
    """Testes para NotificationUseCaseInterface"""

    def test_interface_is_abstract(self):
        """Testa que a interface é abstrata"""
        with pytest.raises(TypeError):
            NotificationUseCaseInterface()

    def test_interface_has_execute_method(self):
        """Testa que a interface tem o método execute"""
        assert hasattr(NotificationUseCaseInterface, 'execute')

    def test_concrete_implementation_use_case(self):
        """Testa implementação concreta do use case"""

        class ConcreteNotificationUseCase(NotificationUseCaseInterface):
            def __init__(self):
                self.executed = False

            def execute(self, dto: NotificationDto) -> None:
                self.executed = True

        use_case = ConcreteNotificationUseCase()
        dto = MagicMock(spec=NotificationDto)

        use_case.execute(dto)

        assert use_case.executed is True

