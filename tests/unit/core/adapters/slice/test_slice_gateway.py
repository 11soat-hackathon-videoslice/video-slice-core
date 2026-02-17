"""Testes unitários para VdscGateway"""
import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime
from core.adapters.slice.slice_gateway import SliceGateway
from core.domain.vdsc_metadata import VdscMetadata
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO
from core.domain.notification import Notification, NotificationContent, EmailPayload, WebPayload
from core.enums.notification_channels_enum import NotificationChannelsEnum
from core.enums.email_template_enum import EmailTemplateEnum


@pytest.mark.unit
class TestSliceGateway:
    """Testes para o Gateway"""

    @pytest.fixture
    def mock_dataproxy(self):
        """Mock para DataProxy"""
        return Mock()

    @pytest.fixture
    def gateway(self, mock_dataproxy):
        """Fixture para criar instância do Gateway"""
        return SliceGateway(dataproxy=mock_dataproxy)

    @pytest.fixture
    def valid_dto(self):
        """Fixture com DTO válido"""
        return VdscMetadataDTO(
            video_id="video123",
            file_name="test_video.mp4",
            file_extension="mp4",
            status="uploaded",
            created="2026-01-13T00:00:00Z",
            user_id="user123",
            total_time=3600,
            unit_time="s",
            start_time=0,
            end_time=60,
            interval_time=["00:00:00", "00:01:00"],
            max_retries=3,
            retries=0,
            resize="high",
            quality_output_level=77,
            logs=[]
        )

    def test_init(self, gateway, mock_dataproxy):
        """Testa inicialização do gateway"""
        assert gateway.dataproxy == mock_dataproxy

    def test_delete_file(self, gateway, mock_dataproxy):
        """Testa deleção de arquivo"""
        gateway.delete_file("test/file.txt")
        mock_dataproxy.delete_file.assert_called_once_with("test/file.txt")

    def test_open_file(self, gateway, mock_dataproxy):
        """Testa abertura de arquivo"""
        mock_dataproxy.open_file.return_value = b"file content"
        result = gateway.open_file(file_path="test/file.txt")
        assert result == b"file content"
        mock_dataproxy.open_file.assert_called_once_with("test/file.txt")

    def test_save_file(self, gateway, mock_dataproxy):
        """Testa salvamento de arquivo"""
        gateway.save_file(file_path="test/file.txt", data=b"content")
        mock_dataproxy.save_file.assert_called_once_with("test/file.txt", b"content")

    def test_update_metadata_by_video_id(self, gateway, mock_dataproxy, valid_dto):
        """Testa atualização de metadados"""
        mock_metadata = VdscMetadata(dto=valid_dto)
        mock_dataproxy.update_metadata_by_video_id.return_value = valid_dto

        result = gateway.update_metadata(mock_metadata)

        assert isinstance(result, VdscMetadata)
        mock_dataproxy.update_metadata_by_video_id.assert_called_once()

    def test_send_notification_with_email_and_web(self, gateway, mock_dataproxy, valid_dto):
        """Testa envio de notificação com email e web"""
        # Preparar notificação
        metadata = VdscMetadata(dto=valid_dto)
        notification = Notification(
            id=uuid4(),
            channels=[NotificationChannelsEnum.EMAIL, NotificationChannelsEnum.WEB],
            metadata=metadata,
            content=[NotificationContent(
                email=EmailPayload(user_id="user123", template=EmailTemplateEnum.PROCESSING),
                web=WebPayload(user_id="user123", message="Test message", timestamp=datetime.now())
            )]
        )

        # Executar
        gateway.send_notification(notification)

        # Verificar
        mock_dataproxy.send_notification.assert_called_once()
        args = mock_dataproxy.send_notification.call_args[0]
        assert str(args[0].id) == str(notification.id)
        assert args[0].channels == notification.channels

    def test_send_notification_email_only(self, gateway, mock_dataproxy, valid_dto):
        """Testa envio de notificação apenas por email"""
        metadata = VdscMetadata(dto=valid_dto)
        notification = Notification(
            id=uuid4(),
            channels=[NotificationChannelsEnum.EMAIL],
            metadata=metadata,
            content=[NotificationContent(
                email=EmailPayload(user_id="user123", template=EmailTemplateEnum.FINISHED)
            )]
        )

        gateway.send_notification(notification)

        mock_dataproxy.send_notification.assert_called_once()
        args = mock_dataproxy.send_notification.call_args[0]
        assert str(args[0].id) == str(notification.id)
        assert NotificationChannelsEnum.EMAIL in args[0].channels

    def test_send_notification_web_only(self, gateway, mock_dataproxy, valid_dto):
        """Testa envio de notificação apenas por web"""
        metadata = VdscMetadata(dto=valid_dto)
        notification = Notification(
            id=uuid4(),
            channels=[NotificationChannelsEnum.WEB],
            metadata=metadata,
            content=[NotificationContent(
                web=WebPayload(user_id="user123", message="Web only message", timestamp=datetime.now())
            )]
        )

        gateway.send_notification(notification)

        mock_dataproxy.send_notification.assert_called_once()
        args = mock_dataproxy.send_notification.call_args[0]
        assert str(args[0].id) == str(notification.id)
        assert NotificationChannelsEnum.WEB in args[0].channels

    def test_send_schedule_retry_event(self, gateway, mock_dataproxy, valid_dto):
        """Testa envio de evento de retry agendado"""
        metadata = VdscMetadata(dto=valid_dto)
        schedule_time = datetime(2026, 2, 8, 12, 0, 0)
        schedule_config = {
            "retry_arn": "arn:aws:events:us-east-1:123456789:rule/retry",
            "retry_role_arn": "arn:aws:iam::123456789:role/retry",
            "retry_dlq": "https://sqs.us-east-1.amazonaws.com/123456789/retry-dlq"
        }

        gateway.send_schedule_retry_event(metadata, schedule_time, schedule_config)

        mock_dataproxy.send_schedule_retry_event.assert_called_once()
        args = mock_dataproxy.send_schedule_retry_event.call_args[0]
        assert isinstance(args[0], VdscMetadataDTO)
        assert args[1] == schedule_time
        assert args[2] == schedule_config

