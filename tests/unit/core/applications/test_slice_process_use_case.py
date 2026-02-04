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
        config = MagicMock(spec=VdscConfigDTO)
        config.s3_bucket = {
            "dir_uploads": "uploads/",
            "dir_processing": "processing/",
            "dir_finished": "finished/"
        }
        config.vdsc = {
            "zip_compression_level": 6,
            "png_compression_level": 3,
            "quality": {"high": 720, "medium": 480, "low": 360},
            "schedule_event_rules": {
                "retry_backoff_factor": 2
            }
        }
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
        mock_gateway.get_list_paths_by_directory.return_value = []

        use_case.execute(mock_gateway, valid_event_dto, mock_config, mock_handler)

        assert mock_gateway.update_metadata.called
        assert mock_gateway.move_file.called
        assert mock_gateway.create_directory.called

    def test_execute_with_error_retries_not_exceeded(self, use_case, mock_gateway, mock_config, valid_event_dto, mock_handler):
        """Testa execução com erro quando tentativas não foram excedidas"""
        mock_gateway.move_file.side_effect = Exception("Erro de teste")

        with pytest.raises(VdscException) as exc_info:
            use_case.execute(mock_gateway, valid_event_dto, mock_config, mock_handler)

        assert "Falha no processamento do video video123" in str(exc_info.value)
        assert mock_gateway.send_schedule_retry_event.called

    def test_execute_with_error_max_retries_reached(self, use_case, mock_gateway, mock_config, valid_event_dto, mock_handler):
        """Testa execução com erro quando máximo de tentativas foi alcançado"""
        valid_event_dto.retries = 3
        valid_event_dto.max_retry = 3
        mock_gateway.move_file.side_effect = Exception("Erro de teste")

        with pytest.raises(VdscException) as exc_info:
            use_case.execute(mock_gateway, valid_event_dto, mock_config, mock_handler)

        assert "Processamento do video video123 falhou após 3 tentativas" in str(exc_info.value)
