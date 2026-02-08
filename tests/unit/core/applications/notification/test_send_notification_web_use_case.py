"""Testes unitários para SendNotificationWebUseCase"""
import pytest
from unittest.mock import Mock
from datetime import datetime, UTC
from uuid import uuid4
from core.applications.notification.send_notification_web_use_case import SendNotificationWebUseCase
from core.dtos.notification_dto import NotificationDto, NotificationContentDto, WebPayloadDto, EmailPayloadDto
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO
from core.enums.notification_channels_enum import NotificationChannelsEnum
from core.enums.email_template_enum import EmailTemplateEnum
from core.interfaces.notification.notication_interfaces import NotificationGatewayInterface


@pytest.mark.unit
class TestSendNotificationWebUseCase:
    """Testes para SendNotificationWebUseCase"""

    @pytest.fixture
    def mock_gateway(self):
        """Fixture com gateway mockado"""
        return Mock(spec=NotificationGatewayInterface)

    @pytest.fixture
    def valid_metadata_dto(self):
        """Fixture com metadados válidos"""
        return VdscMetadataDTO(
            video_id="video123",
            file_name="test_video.mp4",
            extension_file="mp4",
            status="UPLOADED",
            created="2026-01-13T00:00:00Z",
            user_id="user123",
            total_time=3600,
            unit_time="s",
            start_time=0,
            end_time=60,
            time_interval=["00:00:00", "00:01:00"],
            max_retry=3,
            retries=0,
            quality="high",
            logs=[]
        )

    def test_execute_with_web_channel_calls_gateway(self, mock_gateway, valid_metadata_dto):
        use_case = SendNotificationWebUseCase()
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayloadDto(
            user_id="user123",
            message="Processamento concluído",
            timestamp=timestamp,
            is_read=False
        )
        content = NotificationContentDto(web=web)
        notification = NotificationDto(
            id=str(uuid4()),
            channels=[NotificationChannelsEnum.WEB],
            metadata=valid_metadata_dto,
            content=[content]
        )
        use_case.execute(notification, mock_gateway)
        mock_gateway.send.assert_called_once()

    def test_execute_with_wrong_channel_raises_error(self, mock_gateway, valid_metadata_dto):
        use_case = SendNotificationWebUseCase()
        email = EmailPayloadDto(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        content = NotificationContentDto(email=email)
        notification = NotificationDto(
            id=str(uuid4()),
            channels=[NotificationChannelsEnum.EMAIL],
            metadata=valid_metadata_dto,
            content=[content]
        )
        with pytest.raises(ValueError, match="Canal inválido para este caso de uso. Esperado: WEB"):
            use_case.execute(notification, mock_gateway)

    def test_execute_converts_dto_to_domain(self, mock_gateway, valid_metadata_dto):
        use_case = SendNotificationWebUseCase()
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayloadDto(
            user_id="user456",
            message="Teste mensagem",
            timestamp=timestamp,
            is_read=True
        )
        content = NotificationContentDto(web=web)
        notification = NotificationDto(
            id=str(uuid4()),
            channels=[NotificationChannelsEnum.WEB],
            metadata=valid_metadata_dto,
            content=[content]
        )
        use_case.execute(notification, mock_gateway)
        from core.domain.notification import Notification
        call_args = mock_gateway.send.call_args[0][0]
        assert isinstance(call_args, Notification)

    def test_execute_with_unread_notification_works_correctly(self, mock_gateway, valid_metadata_dto):
        use_case = SendNotificationWebUseCase()
        timestamp = datetime(2026, 1, 13, 0, 0, 0, tzinfo=UTC)
        web = WebPayloadDto(
            user_id="user789",
            message="Nova notificação",
            timestamp=timestamp,
            is_read=False
        )
        content = NotificationContentDto(web=web)
        notification = NotificationDto(
            id=str(uuid4()),
            channels=[NotificationChannelsEnum.WEB],
            metadata=valid_metadata_dto,
            content=[content]
        )
        use_case.execute(notification, mock_gateway)
        mock_gateway.send.assert_called_once()

    def test_execute_with_read_notification_works_correctly(self, mock_gateway, valid_metadata_dto):
        use_case = SendNotificationWebUseCase()
        timestamp = datetime(2026, 3, 15, 18, 30, 45, tzinfo=UTC)
        web = WebPayloadDto(
            user_id="user999",
            message="Notificação lida",
            timestamp=timestamp,
            is_read=True
        )
        content = NotificationContentDto(web=web)
        notification = NotificationDto(
            id=str(uuid4()),
            channels=[NotificationChannelsEnum.WEB],
            metadata=valid_metadata_dto,
            content=[content]
        )
        use_case.execute(notification, mock_gateway)
        mock_gateway.send.assert_called_once()

    def test_execute_propagates_gateway_exception(self, mock_gateway, valid_metadata_dto):
        use_case = SendNotificationWebUseCase()
        mock_gateway.send.side_effect = Exception("Erro no gateway")
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayloadDto(
            user_id="user123",
            message="Teste",
            timestamp=timestamp,
            is_read=False
        )
        content = NotificationContentDto(web=web)
        notification = NotificationDto(
            id=str(uuid4()),
            channels=[NotificationChannelsEnum.WEB],
            metadata=valid_metadata_dto,
            content=[content]
        )
        with pytest.raises(Exception, match="Erro no gateway"):
            use_case.execute(notification, mock_gateway)

    def test_execute_with_multiple_web_contents_calls_gateway(self, mock_gateway, valid_metadata_dto):
        use_case = SendNotificationWebUseCase()
        timestamp1 = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        timestamp2 = datetime(2026, 2, 8, 13, 0, 0, tzinfo=UTC)
        web1 = WebPayloadDto(
            user_id="user123",
            message="Primeira notificação",
            timestamp=timestamp1,
            is_read=False
        )
        web2 = WebPayloadDto(
            user_id="user456",
            message="Segunda notificação",
            timestamp=timestamp2,
            is_read=False
        )
        content1 = NotificationContentDto(web=web1)
        content2 = NotificationContentDto(web=web2)
        notification = NotificationDto(
            id=str(uuid4()),
            channels=[NotificationChannelsEnum.WEB],
            metadata=valid_metadata_dto,
            content=[content1, content2]
        )
        use_case.execute(notification, mock_gateway)
        mock_gateway.send.assert_called_once()

    def test_execute_with_long_message_works_correctly(self, mock_gateway, valid_metadata_dto):
        use_case = SendNotificationWebUseCase()
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        long_message = "Esta é uma mensagem muito longa que contém muitos caracteres para testar o comportamento do sistema com mensagens extensas"
        web = WebPayloadDto(
            user_id="user111",
            message=long_message,
            timestamp=timestamp,
            is_read=False
        )
        content = NotificationContentDto(web=web)
        notification = NotificationDto(
            id=str(uuid4()),
            channels=[NotificationChannelsEnum.WEB],
            metadata=valid_metadata_dto,
            content=[content]
        )
        use_case.execute(notification, mock_gateway)
        mock_gateway.send.assert_called_once()

