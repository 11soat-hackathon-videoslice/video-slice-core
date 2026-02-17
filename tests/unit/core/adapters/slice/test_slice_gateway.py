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

    def test_send_metric(self, gateway, mock_dataproxy):
        """Testa envio de métricas"""
        metric_info = {
            'resize': True,
            'original_min_size': 1080,
            'resize_output': 720,
            'quality_output_level': 'high',
            'frames_processed': 10,
            'workers': 4,
            'video_size_mb': 100.0,
            'process_total_time_seconds': 15.5,
            'efficiency_per_frame_seconds': 1.55
        }

        gateway.send_metric(metric_info)

        mock_dataproxy.send_metric.assert_called_once_with(metric_info)

    def test_send_metric_with_different_quality_levels(self, gateway, mock_dataproxy):
        """Testa envio de métricas com diferentes níveis de qualidade"""
        quality_levels = ['ultra', 'high', 'medium', 'low']

        for quality in quality_levels:
            metric_info = {
                'resize': True,
                'original_min_size': 1080,
                'resize_output': 720,
                'quality_output_level': quality,
                'frames_processed': 5,
                'workers': 2,
                'video_size_mb': 50.0,
                'process_total_time_seconds': 10.0,
                'efficiency_per_frame_seconds': 2.0
            }

            gateway.send_metric(metric_info)

        assert mock_dataproxy.send_metric.call_count == len(quality_levels)

    def test_send_metric_without_resize(self, gateway, mock_dataproxy):
        """Testa envio de métricas sem redimensionamento"""
        metric_info = {
            'resize': False,
            'original_min_size': 720,
            'resize_output': 720,
            'quality_output_level': 'original',
            'frames_processed': 3,
            'workers': 1,
            'video_size_mb': 25.5,
            'process_total_time_seconds': 5.2,
            'efficiency_per_frame_seconds': 1.73
        }

        gateway.send_metric(metric_info)

        mock_dataproxy.send_metric.assert_called_once_with(metric_info)

    def test_send_metric_with_large_number_of_frames(self, gateway, mock_dataproxy):
        """Testa envio de métricas com grande número de frames"""
        metric_info = {
            'resize': True,
            'original_min_size': 1080,
            'resize_output': 480,
            'quality_output_level': 'medium',
            'frames_processed': 500,
            'workers': 8,
            'video_size_mb': 750.0,
            'process_total_time_seconds': 300.0,
            'efficiency_per_frame_seconds': 0.6
        }

        gateway.send_metric(metric_info)

        mock_dataproxy.send_metric.assert_called_once_with(metric_info)
        args = mock_dataproxy.send_metric.call_args[0]
        assert args[0]['frames_processed'] == 500
        assert args[0]['workers'] == 8
