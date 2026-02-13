"""Testes unitários para SliceProcessUseCase"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from core.applications.slice_process_use_case import SliceProcessUseCase
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO
from core.dtos.vdsc_config_dto import VdscConfigDTO
from core.exceptions.vdsc_exceptions import VdscException


@pytest.mark.unit
class TestSliceProcessUseCase:
    """Testes para o caso de uso de processamento de vídeo"""

    @pytest.fixture
    def use_case(self):
        """Fixture do use case"""
        return SliceProcessUseCase()

    @pytest.fixture
    def mock_gateway(self):
        """Fixture do gateway mockado"""
        gateway = Mock()
        gateway.update_metadata = Mock()
        gateway.update_metadata_by_video_id = Mock()
        gateway.move_file = Mock()
        gateway.create_directory = Mock()
        gateway.open_file = Mock(return_value=b"fake_video_data")
        gateway.delete_files_by_directory = Mock()
        gateway.delete_file = Mock()
        gateway.save_file = Mock()
        gateway.send_event = Mock()
        gateway.send_schedule_retry_event = Mock()
        gateway.send_notification = Mock()
        gateway.get_list_paths_by_directory = Mock(return_value=[])
        return gateway

    @pytest.fixture
    def mock_config(self):
        """Fixture da configuração"""
        # Mock para QualityDTO
        quality_mock = MagicMock()
        quality_mock.ultra = 1080
        quality_mock.high = 720
        quality_mock.medium = 480
        quality_mock.low = 360

        # Mock para ScheduleRulesDTO
        schedule_rules_mock = MagicMock()
        schedule_rules_mock.retry_backoff_factor = 2
        schedule_rules_mock.retry_arn = "arn:aws:events:us-east-1:123456789:rule/retry"
        schedule_rules_mock.retry_role_arn = "arn:aws:iam::123456789:role/retry"
        schedule_rules_mock.retry_dlq = "https://sqs.us-east-1.amazonaws.com/123456789/retry-dlq"

        # Mock para VdscSettingsDTO
        vdsc_settings_mock = MagicMock()
        vdsc_settings_mock.zip_compression_level = 6
        vdsc_settings_mock.png_compression_level = 3
        vdsc_settings_mock.max_workers = 10
        vdsc_settings_mock.quality = quality_mock
        vdsc_settings_mock.schedule_event_rules = schedule_rules_mock

        # Mock para S3ConfigDTO
        s3_config_mock = MagicMock()
        s3_config_mock.bucket_name = "test-bucket"
        s3_config_mock.dir_uploads = "uploads/"
        s3_config_mock.dir_processing = "processing/"
        s3_config_mock.dir_finished = "finished/"

        # Mock para VdscConfigDTO
        config = MagicMock(spec=VdscConfigDTO)
        config.aws_region = "us-east-1"
        config.dynamodb_table_name = "VideoSlice"
        config.event_bus_name = "default"
        config.s3_bucket = s3_config_mock
        config.vdsc = vdsc_settings_mock

        return config

    @pytest.fixture
    def valid_event_dto(self):
        """Fixture com evento válido"""
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
            time_interval=[10],
            max_retry=3,
            retries=0,
            quality="high",
            logs=[]
        )

    @pytest.fixture
    def mock_handler(self):
        """Fixture do exception handler"""
        handler = Mock()
        handler.vdsc_exception_handler = lambda func: func
        return handler


    @patch('core.utils.slice_process_util.cv2.VideoCapture')
    def test_execute_success(self, mock_video_capture, use_case, mock_gateway, mock_config, valid_event_dto, mock_handler):
        """Testa execução completa com sucesso"""
        import numpy as np

        # Mock do video capture
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_cap.read.return_value = (True, np.zeros((720, 1280, 3), dtype=np.uint8))

        # Mock do update para retornar VdscMetadata
        def mock_update(metadata):
            return metadata
        mock_gateway.update_metadata.side_effect = mock_update
        mock_gateway.open_file.return_value = b"fake_video_data"
        mock_gateway.upload_zip_file = Mock()

        use_case.execute(mock_gateway, valid_event_dto, mock_config, mock_handler)

        assert mock_gateway.update_metadata.called
        assert mock_gateway.open_file.called
        assert mock_gateway.upload_zip_file.called
        assert mock_gateway.delete_file.called
        assert mock_gateway.send_notification.called

    def test_execute_with_error_retries_not_exceeded(self, use_case, mock_gateway, mock_config, valid_event_dto, mock_handler):
        """Testa execução com erro quando tentativas não foram excedidas"""
        mock_gateway.move_file.side_effect = Exception("Erro de teste")

        with pytest.raises(VdscException) as exc_info:
            use_case.execute(mock_gateway, valid_event_dto, mock_config, mock_handler)

        assert "video123 - Falha no processamento do video test_video.mp4.mp4" in str(exc_info.value)
        assert mock_gateway.send_schedule_retry_event.called

    def test_execute_with_error_max_retries_reached(self, use_case, mock_gateway, mock_config, valid_event_dto, mock_handler):
        """Testa execução com erro quando máximo de tentativas foi alcançado"""
        valid_event_dto.retries = 3
        valid_event_dto.max_retry = 3
        mock_gateway.move_file.side_effect = Exception("Erro de teste")

        with pytest.raises(VdscException) as exc_info:
            use_case.execute(mock_gateway, valid_event_dto, mock_config, mock_handler)

        assert " video123 - Processamento do video test_video.mp4.mp4 falhou após 3 tentativas" in str(exc_info.value)
