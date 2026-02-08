"""Testes unitários para NotificationGateway"""
import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime, UTC
from core.adapters.notification.notification_gateway import NotificationGateway
from core.domain.notification import Notification, NotificationContent, EmailPayload, WebPayload
from core.domain.vdsc_metadata import VdscMetadata
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO
from core.dtos.notification_dto import NotificationDto
from core.enums.notification_channels_enum import NotificationChannelsEnum
from core.enums.email_template_enum import EmailTemplateEnum
from core.interfaces.notification.notication_interfaces import NotificationDatasourceInterface


@pytest.mark.unit
class TestNotificationGateway:
    """Testes para NotificationGateway"""

    @pytest.fixture
    def mock_datasource(self):
        """Fixture com datasource mockado"""
        return Mock(spec=NotificationDatasourceInterface)

    @pytest.fixture
    def valid_metadata(self):
        """Fixture com metadados válidos"""
        dto = VdscMetadataDTO(
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
        return VdscMetadata(dto=dto)

    def test_gateway_created_with_datasource_successfully(self, mock_datasource):
        gateway = NotificationGateway(mock_datasource)
        assert gateway.datasource == mock_datasource

    def test_send_email_notification_calls_datasource(self, mock_datasource, valid_metadata):
        gateway = NotificationGateway(mock_datasource)
        email = EmailPayload(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        content = NotificationContent(email=email)
        notification = Notification(
            id=uuid4(),
            channels=[NotificationChannelsEnum.EMAIL],
            metadata=valid_metadata,
            content=[content]
        )
        gateway.send(notification)
        mock_datasource.send.assert_called_once()

    def test_send_web_notification_calls_datasource(self, mock_datasource, valid_metadata):
        gateway = NotificationGateway(mock_datasource)
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayload(
            user_id="user123",
            message="Teste",
            timestamp=timestamp,
            is_read=False
        )
        content = NotificationContent(web=web)
        notification = Notification(
            id=uuid4(),
            channels=[NotificationChannelsEnum.WEB],
            metadata=valid_metadata,
            content=[content]
        )
        gateway.send(notification)
        mock_datasource.send.assert_called_once()

    def test_send_notification_converts_domain_to_dto(self, mock_datasource, valid_metadata):
        gateway = NotificationGateway(mock_datasource)
        email = EmailPayload(
            user_id="user123",
            template=EmailTemplateEnum.FINISHED
        )
        content = NotificationContent(email=email)
        notification = Notification(
            id=uuid4(),
            channels=[NotificationChannelsEnum.EMAIL],
            metadata=valid_metadata,
            content=[content]
        )
        gateway.send(notification)
        call_args = mock_datasource.send.call_args[0][0]
        assert isinstance(call_args, NotificationDto)

    def test_send_notification_with_multiple_channels_calls_datasource(self, mock_datasource, valid_metadata):
        gateway = NotificationGateway(mock_datasource)
        email = EmailPayload(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayload(
            user_id="user123",
            message="Teste",
            timestamp=timestamp,
            is_read=False
        )
        content = NotificationContent(email=email, web=web)
        notification = Notification(
            id=uuid4(),
            channels=[NotificationChannelsEnum.EMAIL, NotificationChannelsEnum.WEB],
            metadata=valid_metadata,
            content=[content]
        )
        gateway.send(notification)
        assert mock_datasource.send.call_count == 1

    def test_send_notification_propagates_datasource_exception(self, mock_datasource, valid_metadata):
        gateway = NotificationGateway(mock_datasource)
        mock_datasource.send.side_effect = Exception("Erro no datasource")
        email = EmailPayload(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        content = NotificationContent(email=email)
        notification = Notification(
            id=uuid4(),
            channels=[NotificationChannelsEnum.EMAIL],
            metadata=valid_metadata,
            content=[content]
        )
        with pytest.raises(Exception, match="Erro no datasource"):
            gateway.send(notification)

    def test_send_notification_with_multiple_contents_calls_datasource(self, mock_datasource, valid_metadata):
        gateway = NotificationGateway(mock_datasource)
        email1 = EmailPayload(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        email2 = EmailPayload(
            user_id="user456",
            template=EmailTemplateEnum.FINISHED
        )
        content1 = NotificationContent(email=email1)
        content2 = NotificationContent(email=email2)
        notification = Notification(
            id=uuid4(),
            channels=[NotificationChannelsEnum.EMAIL],
            metadata=valid_metadata,
            content=[content1, content2]
        )
        gateway.send(notification)
        mock_datasource.send.assert_called_once()

