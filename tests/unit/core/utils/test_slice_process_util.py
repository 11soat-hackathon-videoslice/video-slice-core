"""Testes unitários para slice_process_util"""
import pytest
import io
import zipfile
import sys
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from uuid import UUID

# Mock cv2 to avoid import issues
sys.modules['cv2'] = MagicMock()

from core.utils.slice_process_util import (
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
    get_frame_new_size,
    metadata_update_status,
    process_video,
    process_video_frame,
    set_exception_status,
    create_notification,
    create_email_notification,
    create_web_notification
)
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO
from core.dtos.vdsc_config_dto import VdscConfigDTO
from core.enums.vdsc_status_enum import VdscStatusEnum
from core.enums.email_template_enum import EmailTemplateEnum
from core.enums.notification_channels_enum import NotificationChannelsEnum
from core.domain.vdsc_metadata import VdscMetadata, LogEntry
from core.domain.notification import Notification, EmailPayload, WebPayload


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
        vdsc_settings_mock.dir_uploads = "uploads"
        vdsc_settings_mock.dir_finished = "finished"
        vdsc_settings_mock.dir_tmp = "/tmp"
        vdsc_settings_mock.zip_compression_level = 6
        vdsc_settings_mock.png_compression_level = 3
        vdsc_settings_mock.max_workers = 4
        vdsc_settings_mock.quality = quality_mock
        vdsc_settings_mock.schedule_event_rules = schedule_rules_mock

        # Mock para VdscConfigDTO
        config = MagicMock(spec=VdscConfigDTO)
        config.aws_region = "us-east-1"
        config.s3_bucket_name= "test-bucket"
        config.dynamodb_table_name = "VideoSlice"
        config.event_bus_name = "default"
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
        result = get_path_file(mock_config.vdsc.dir_uploads, "video123", "mp4")
        assert result == "uploads/video123.mp4"

    def test_get_path_directory(self, mock_config):
        """Testa geração de caminho de diretório"""
        result = get_path_directory(mock_config.vdsc.dir_tmp, "video123")
        assert result == "/tmp/video123/"

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

    def test_get_frame_new_size(self):
        """Testa cálculo de novo tamanho de frame"""
        import numpy as np
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

        new_width, new_height = get_frame_new_size(frame, 720)

        assert new_width == 1280
        assert new_height == 720

    def test_get_frame_new_size_no_resize_needed(self):
        """Testa quando frame já está no tamanho correto"""
        import numpy as np
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

        new_width, new_height = get_frame_new_size(frame, 1080)

        assert new_width == 1920
        assert new_height == 1080

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


    @patch('core.utils.slice_process_util.cv2.VideoCapture')
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

        process_video(metadata, b"fake_data", "processing/video123/", mock_gateway, mock_config)

        assert mock_gateway.save_file.called

    @patch('core.utils.slice_process_util.cv2.VideoCapture')
    def test_process_video_frames_failure(self, mock_video_capture, mock_gateway, mock_config, valid_event_dto):
        """Testa processamento de frames com falha na leitura"""
        # Mock do video capture com falha
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_cap.read.return_value = (False, None)

        metadata = VdscMetadata(dto=valid_event_dto)
        metadata.time_interval = [1]
        metadata.quality = "none"  # To avoid resize check
        mock_config.vdsc.quality.none = None  # Make getattr return None

        process_video(metadata, b"fake_data", "processing/video123/", mock_gateway, mock_config)

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
        assert "Criando tentativa 2 de 3" in message
        assert mock_gateway.send_schedule_retry_event.called

    def test_set_exception_status_failed_direct(self, mock_gateway, mock_config, valid_event_dto):
        """Testa função set_exception_status_failed diretamente"""
        metadata = VdscMetadata(dto=valid_event_dto)
        metadata.max_retry = 3
        ex = Exception("Erro crítico")

        result_metadata, message = set_exception_status(mock_gateway, ex, metadata, VdscStatusEnum.FAILED, mock_config)

        assert result_metadata.status == VdscStatusEnum.FAILED.value
        assert "falhou após 3 tentativas" in message
        assert "Erro crítico" in message
        assert mock_gateway.send_notification.called
        mock_gateway.send_notification.assert_called_once()

    def test_set_exception_status_retrying_direct(self, mock_gateway, mock_config, valid_event_dto):
        """Testa função set_exception_status_retrying diretamente"""
        metadata = VdscMetadata(dto=valid_event_dto)
        metadata.retries = 0
        metadata.max_retry = 3
        ex = Exception("Erro temporário")

        result_metadata, message = set_exception_status(mock_gateway, ex, metadata, VdscStatusEnum.RETRYING, mock_config)

        assert result_metadata.status == VdscStatusEnum.RETRYING.value
        assert "Criando tentativa 1 de 3" in message
        assert "Erro temporário" in message
        assert mock_gateway.send_schedule_retry_event.called
        assert mock_gateway.send_notification.called

    def test_create_email_notification(self, valid_event_dto):
        """Testa criação de payload de email"""
        metadata = VdscMetadata(dto=valid_event_dto)

        result = create_email_notification(metadata, EmailTemplateEnum.UPDATE_STATUS)

        assert isinstance(result, EmailPayload)
        assert result.user_id == "user123"
        assert result.template == EmailTemplateEnum.UPDATE_STATUS

    def test_create_email_notification_finished(self, valid_event_dto):
        """Testa criação de payload de email com template FINISHED"""
        metadata = VdscMetadata(dto=valid_event_dto)

        result = create_email_notification(metadata, EmailTemplateEnum.FINISHED)

        assert isinstance(result, EmailPayload)
        assert result.user_id == "user123"
        assert result.template == EmailTemplateEnum.FINISHED

    def test_create_web_notification(self, valid_event_dto):
        """Testa criação de payload de notificação web"""
        metadata = VdscMetadata(dto=valid_event_dto)
        message = "Processamento em andamento"

        result = create_web_notification(metadata, message)

        assert isinstance(result, WebPayload)
        assert result.user_id == "user123"
        assert result.message == message
        assert isinstance(result.timestamp, datetime)
        assert result.is_read is False

    def test_create_notification_with_email_and_web(self, valid_event_dto):
        """Testa criação de notificação completa com email e web"""
        metadata = VdscMetadata(dto=valid_event_dto)
        message = "Vídeo processado com sucesso"

        result = create_notification(metadata, ['email', 'web'], message, EmailTemplateEnum.FINISHED)

        assert isinstance(result, Notification)
        assert isinstance(result.id, UUID)
        assert NotificationChannelsEnum.EMAIL in result.channels
        assert NotificationChannelsEnum.WEB in result.channels
        assert len(result.content) == 1
        assert result.content[0].email is not None
        assert result.content[0].web is not None
        assert result.content[0].email.template == EmailTemplateEnum.FINISHED
        assert result.content[0].web.message == message

    def test_create_notification_email_only(self, valid_event_dto):
        """Testa criação de notificação apenas com email"""
        metadata = VdscMetadata(dto=valid_event_dto)

        result = create_notification(metadata, ['email'], None, EmailTemplateEnum.FAILED)

        assert isinstance(result, Notification)
        assert NotificationChannelsEnum.EMAIL in result.channels
        assert len(result.content) == 1
        assert result.content[0].email is not None
        assert result.content[0].web is None

    def test_create_notification_web_only(self, valid_event_dto):
        """Testa criação de notificação apenas com web"""
        metadata = VdscMetadata(dto=valid_event_dto)
        message = "Notificação apenas web"

        result = create_notification(metadata, ['web'], message, None)

        assert isinstance(result, Notification)
        assert NotificationChannelsEnum.WEB in result.channels
        assert len(result.content) == 1
        assert result.content[0].email is None
        assert result.content[0].web is not None
        assert result.content[0].web.message == message

    def test_create_notification_empty_content(self, valid_event_dto):
        """Testa criação de notificação sem conteúdo deve falhar se canal requer payload"""
        metadata = VdscMetadata(dto=valid_event_dto)

        # Deve lançar exceção, pois canal EMAIL requer EmailPayload
        with pytest.raises(ValueError, match="Canal EMAIL requer EmailPayload"):
            create_notification(metadata, ['email'], None, None)

    @patch('core.utils.slice_process_util.cv2.VideoCapture')
    def test_process_video_frame_success_with_resize(self, mock_video_capture, mock_gateway, mock_config, valid_event_dto):
        """Testa processamento de um frame com sucesso e redimensionamento"""
        import numpy as np

        # Mock do video capture
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_cap.read.return_value = (True, np.zeros((1080, 1920, 3), dtype=np.uint8))

        metadata = VdscMetadata(dto=valid_event_dto)

        result = process_video_frame(
            1000, "test_video.mp4", {"resize": True, "new_width": 1280, "new_height": 720}, metadata, "processing/video123/", "high", "video123", 1000, 3, mock_gateway
        )

        assert "Sucesso" in result
        assert mock_gateway.save_file.called

    @patch('core.utils.slice_process_util.cv2.VideoCapture')
    def test_process_video_frame_success_without_resize(self, mock_video_capture, mock_gateway, mock_config, valid_event_dto):
        """Testa processamento de um frame com sucesso sem redimensionamento"""
        import numpy as np

        # Mock do video capture
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_cap.read.return_value = (True, np.zeros((720, 1280, 3), dtype=np.uint8))

        metadata = VdscMetadata(dto=valid_event_dto)

        result = process_video_frame(
            1000, "test_video.mp4", {"resize": False, "new_width": None, "new_height": None}, metadata, "processing/video123/", "high", "video123", 1000, 3, mock_gateway
        )

        assert "Sucesso" in result
        assert mock_gateway.save_file.called

    @patch('core.utils.slice_process_util.cv2.VideoCapture')
    def test_process_video_frame_failure_read(self, mock_video_capture, mock_gateway, mock_config, valid_event_dto):
        """Testa processamento de um frame com falha na leitura"""
        # Mock do video capture com falha
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_cap.read.return_value = (False, None)

        metadata = VdscMetadata(dto=valid_event_dto)

        result = process_video_frame(
            1000, "test_video.mp4", {"resize": False, "new_width": None, "new_height": None}, metadata, "processing/video123/", "high", "video123", 1000, 3, mock_gateway
        )

        assert "Erro" in result
        assert not mock_gateway.save_file.called
