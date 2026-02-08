"""Testes unitários para NotificationController"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, UTC
from uuid import uuid4
from core.adapters.notification.notification_controller import NotificationController
from core.dtos.notification_dto import NotificationDto, NotificationContentDto, EmailPayloadDto, WebPayloadDto
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO
from core.enums.notification_channels_enum import NotificationChannelsEnum
from core.enums.email_template_enum import EmailTemplateEnum
from core.interfaces.notification.notication_interfaces import NotificationDatasourceInterface


@pytest.mark.unit
class TestNotificationController:
    """Testes para NotificationController"""

    @pytest.fixture
    def mock_datasource(self):
        """Fixture com datasource mockado"""
        return Mock(spec=NotificationDatasourceInterface)

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

    def test_controller_created_with_datasource_successfully(self, mock_datasource):
        controller = NotificationController(mock_datasource)
        assert controller.datasource == mock_datasource
        assert controller.factory_use_case is not None

    def test_send_email_notification_executes_use_case(self, mock_datasource, valid_metadata_dto):
        controller = NotificationController(mock_datasource)
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
        with patch.object(controller.factory_use_case, 'get_use_case') as mock_get_use_case:
            mock_use_case = Mock()
            mock_get_use_case.return_value = mock_use_case
            controller.send(notification)
            mock_get_use_case.assert_called_once()
            mock_use_case.execute.assert_called_once()

    def test_send_web_notification_executes_use_case(self, mock_datasource, valid_metadata_dto):
        controller = NotificationController(mock_datasource)
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
        with patch.object(controller.factory_use_case, 'get_use_case') as mock_get_use_case:
            mock_use_case = Mock()
            mock_get_use_case.return_value = mock_use_case
            controller.send(notification)
            mock_get_use_case.assert_called_once()
            mock_use_case.execute.assert_called_once()

    def test_send_notification_retrieves_correct_use_case(self, mock_datasource, valid_metadata_dto):
        controller = NotificationController(mock_datasource)
        email = EmailPayloadDto(
            user_id="user123",
            template=EmailTemplateEnum.FINISHED
        )
        content = NotificationContentDto(email=email)
        notification = NotificationDto(
            id=str(uuid4()),
            channels=[NotificationChannelsEnum.EMAIL],
            metadata=valid_metadata_dto,
            content=[content]
        )
        with patch.object(controller.factory_use_case, 'get_use_case') as mock_get_use_case:
            mock_use_case = Mock()
            mock_get_use_case.return_value = mock_use_case
            controller.send(notification)
            call_args = mock_get_use_case.call_args[0][0]
            assert call_args == NotificationChannelsEnum.EMAIL
            mock_get_use_case.assert_called_once_with(NotificationChannelsEnum.EMAIL)

    def test_send_notification_passes_gateway_to_use_case(self, mock_datasource, valid_metadata_dto):
        controller = NotificationController(mock_datasource)
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
        with patch.object(controller.factory_use_case, 'get_use_case') as mock_get_use_case:
            mock_use_case = Mock()
            mock_get_use_case.return_value = mock_use_case
            controller.send(notification)
            call_args = mock_use_case.execute.call_args
            assert call_args is not None

    def test_send_notification_propagates_use_case_exception(self, mock_datasource, valid_metadata_dto):
        controller = NotificationController(mock_datasource)
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
        with patch.object(controller.factory_use_case, 'get_use_case') as mock_get_use_case:
            mock_use_case = Mock()
            mock_use_case.execute.side_effect = Exception("Erro no use case")
            mock_get_use_case.return_value = mock_use_case
            with pytest.raises(Exception, match="Erro no use case"):
                controller.send(notification)

    def test_send_notification_with_invalid_channel_raises_error(self, mock_datasource, valid_metadata_dto):
        controller = NotificationController(mock_datasource)
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
        with patch.object(controller.factory_use_case, 'get_use_case') as mock_get_use_case:
            mock_get_use_case.side_effect = ValueError("Não encontrado caso de uso para o canal")
            with pytest.raises(ValueError, match="Não encontrado caso de uso para o canal"):
                controller.send(notification)

