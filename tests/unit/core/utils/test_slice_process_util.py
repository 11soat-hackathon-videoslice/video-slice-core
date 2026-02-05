"""Testes unitários para slice_process_util"""
import pytest
import io
import zipfile
from unittest.mock import Mock, MagicMock, patch
from core.utils.slice_process_util import (
    compress_images_to_zip,
    create_temporary_file,
    create_interval_list,
    create_zip_buffer,
    encode_frame_to_png,
    frame_resize,
    get_file_info_list,
    get_multiplier_time_unit,
    get_path_file,
    get_path_directory,
    get_recurrent_time_intervals,
    get_specific_time_intervals,
    get_frame_widths,
    metadata_update_status,
    process_video_frames,
    set_exception_status
)
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO
from core.dtos.vdsc_config_dto import VdscConfigDTO
from core.enums.vdsc_status_enum import VdscStatusEnum
from core.domain.vdsc_metadata import VdscMetadata, LogEntry


@pytest.mark.unit
class TestSliceProcessUtil:
    """Testes para as funções utilitárias de processamento de vídeo"""

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

    def test_get_path_file(self, mock_config):
        """Testa geração de caminho de arquivo"""
        result = get_path_file("uploads/", "video123", "mp4")
        assert result == "uploads/video123.mp4"

    def test_get_path_directory(self, mock_config):
        """Testa geração de caminho de diretório"""
        result = get_path_directory("processing/", "video123")
        assert result == "processing/video123/"

    def test_get_multiplier_time_unit_seconds(self):
        """Testa multiplicador para segundos"""
        result = get_multiplier_time_unit("s")
        assert result == 1000

    def test_get_multiplier_time_unit_milliseconds(self):
        """Testa multiplicador para milissegundos"""
        result = get_multiplier_time_unit("ms")
        assert result == 1

    def test_get_specific_time_intervals(self):
        """Testa conversão de intervalos específicos"""
        result = get_specific_time_intervals([1, 2, 3], 1000)
        assert result == [1000, 2000, 3000]

    def test_get_recurrent_time_intervals(self):
        """Testa geração de intervalos recorrentes"""
        result = get_recurrent_time_intervals(0, 30, 10)
        assert result == [0, 10, 20, 30]

    def test_metadata_update_status(self, valid_event_dto):
        """Testa atualização de status de metadados"""
        metadata = VdscMetadata(dto=valid_event_dto)
        log = LogEntry("Teste de log")

        result = metadata_update_status(metadata, VdscStatusEnum.PROCESSING, log)

        assert result.status == VdscStatusEnum.PROCESSING.value
        assert len(result.logs) == 1

    def test_create_zip_buffer(self):
        """Testa criação de buffer zip"""
        file_list = [("file1.txt", b"content1"), ("file2.txt", b"content2")]

        result = create_zip_buffer(file_list, 6)

        assert isinstance(result, io.BytesIO)
        with zipfile.ZipFile(result, 'r') as zf:
            assert "file1.txt" in zf.namelist()
            assert "file2.txt" in zf.namelist()

    def test_get_file_info_list(self, mock_gateway):
        """Testa obtenção de informações de arquivos"""
        mock_gateway.get_list_paths_by_directory.return_value = [
            "processing/video123/frame1.png",
            "processing/video123/frame2.png"
        ]
        mock_gateway.open_file.side_effect = [b"data1", b"data2"]

        result = get_file_info_list("processing/video123/", mock_gateway)

        assert len(result) == 2
        assert result[0][0] == "frame1.png"
        assert result[1][0] == "frame2.png"

    def test_create_temporary_file(self):
        """Testa criação de arquivo temporário"""
        video_data = b"fake_video_data"

        result = create_temporary_file(video_data, "mp4")

        assert result.endswith(".mp4")
        import os
        assert os.path.exists(result)
        os.remove(result)

    def test_get_frame_widths(self):
        """Testa cálculo de largura de frame"""
        import numpy as np
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

        result, original = get_frame_widths(frame, 720)

        assert result == 1280
        assert original == 1920

    def test_get_frame_widths_no_resize_needed(self):
        """Testa quando frame já está no tamanho correto"""
        import numpy as np
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

        result, original = get_frame_widths(frame, 1080)

        assert result == original

    def test_frame_resize(self):
        """Testa redimensionamento de frame"""
        import numpy as np
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

        result = frame_resize(frame, 1280, 720)

        assert result.shape == (720, 1280, 3)

    def test_encode_frame_to_png(self):
        """Testa codificação de frame para PNG"""
        import numpy as np
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)

        success, data = encode_frame_to_png(frame, 3)

        assert success is True
        assert data is not None

    def test_create_interval_list_recurrent(self, valid_event_dto):
        """Testa criação de lista de intervalos recorrentes"""
        valid_event_dto.time_interval = [5]
        valid_event_dto.start_time = 0
        valid_event_dto.end_time = 20
        metadata = VdscMetadata(dto=valid_event_dto)

        result = create_interval_list(metadata, 1000)

        assert result == [0, 5000, 10000, 15000, 20000]

    def test_create_interval_list_specific(self, valid_event_dto):
        """Testa criação de lista de intervalos específicos"""
        valid_event_dto.time_interval = [5, 10, 15]
        metadata = VdscMetadata(dto=valid_event_dto)

        result = create_interval_list(metadata, 1000)

        assert result == [5000, 10000, 15000]

    def test_compress_images_to_zip(self, mock_gateway, mock_config):
        """Testa compactação de imagens para zip"""
        mock_gateway.get_list_paths_by_directory.return_value = ["processing/video123/frame1.png"]
        mock_gateway.open_file.return_value = b"fake_image_data"

        compress_images_to_zip("processing/video123/", "finished/video123.zip", mock_gateway, mock_config)

        mock_gateway.save_file.assert_called_once()

    @patch('cv2.VideoCapture')
    def test_process_video_frames_success(self, mock_video_capture, mock_gateway, mock_config, valid_event_dto):
        """Testa processamento de frames de vídeo com sucesso"""
        import numpy as np

        # Mock do video capture
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_cap.read.return_value = (True, np.zeros((1080, 1920, 3), dtype=np.uint8))

        metadata = VdscMetadata(dto=valid_event_dto)
        metadata.unit_time = "s"
        metadata.time_interval = [1]
        metadata.start_time = 0
        metadata.end_time = 5

        process_video_frames("video123", metadata, b"fake_data", "processing/video123/", mock_gateway, mock_config)

        assert mock_gateway.save_file.called

    @patch('cv2.VideoCapture')
    def test_process_video_frames_failure(self, mock_video_capture, mock_gateway, mock_config, valid_event_dto):
        """Testa processamento de frames com falha na leitura"""
        # Mock do video capture com falha
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_cap.read.return_value = (False, None)

        metadata = VdscMetadata(dto=valid_event_dto)
        metadata.time_interval = [1]

        process_video_frames("video123", metadata, b"fake_data", "processing/video123/", mock_gateway, mock_config)

        # Não deve salvar arquivo se leitura falhar
        assert not mock_gateway.save_file.called

    def test_set_exception_status_failed(self, mock_gateway, mock_config, valid_event_dto):
        """Testa definição de status FAILED"""
        metadata = VdscMetadata(dto=valid_event_dto)
        metadata.retries = 3
        metadata.max_retry = 3
        ex = Exception("Erro de teste")

        result_metadata, message = set_exception_status(mock_gateway, ex, metadata, VdscStatusEnum.FAILED, mock_config)

        assert result_metadata.status == VdscStatusEnum.FAILED.value
        assert "falhou após 3 tentativas" in message
        assert not mock_gateway.send_schedule_retry_event.called

    def test_set_exception_status_retrying(self, mock_gateway, mock_config, valid_event_dto):
        """Testa definição de status RETRYING"""
        metadata = VdscMetadata(dto=valid_event_dto)
        metadata.retries = 1
        metadata.max_retry = 3
        ex = Exception("Erro de teste")

        result_metadata, message = set_exception_status(mock_gateway, ex, metadata, VdscStatusEnum.RETRYING, mock_config)

        assert result_metadata.status == VdscStatusEnum.RETRYING.value
        assert "Iniciando tentativa 2 de 3" in message
        assert mock_gateway.send_schedule_retry_event.called
