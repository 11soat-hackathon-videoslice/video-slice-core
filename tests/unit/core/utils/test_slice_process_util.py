"""Testes unitários para slice_process_util"""
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from uuid import UUID

import pytest
import sys

# Mock cv2 to avoid import issues
sys.modules['cv2'] = MagicMock()

from core.utils.slice_process_util import (
    create_temporary_file,
    create_interval_list,
    get_multiplier_time_unit,
    get_path_file,
    get_path_directory,
    get_recurrent_interval_times,
    get_specific_interval_times,
    get_frame_new_size,
    metadata_update_status,
    set_exception_status,
    create_notification,
    create_email_notification,
    create_web_notification
)
from core.utils.slice_video_process_frame_util import frame_resize, encode_frame_to_jpg
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
        # Mock para ResizeDTO
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
        vdsc_settings_mock.max_workers = 4
        vdsc_settings_mock.resize = quality_mock
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
            file_extension="mp4",
            status="UPLOADED",
            created="2026-01-13T00:00:00Z",
            user_id="user123",
            total_time=3600,
            unit_time="s",
            start_time=0,
            end_time=60,
            interval_time=[10],
            max_retries=3,
            retries=0,
            resize="high",
            quality_output_level=75,
            logs=[]
        )

    def test_get_path_file(self, mock_config):
        """Testa geração de caminho de arquivo"""
        result = get_path_file(mock_config.vdsc.dir_uploads, "video123", "mp4")
        assert result == "uploads/video123.mp4"

    def test_get_path_file_formats_correctly(self):
        """Testa que get_path_file formata o caminho corretamente"""
        path = get_path_file("uploads", "video123", "mp4")
        assert path == "uploads/video123.mp4"

    def test_get_path_file_with_different_extensions(self):
        """Testa get_path_file com diferentes extensões"""
        extensions = ["mp4", "avi", "mkv", "mov"]
        for ext in extensions:
            path = get_path_file("uploads", "test", ext)
            assert path.endswith(f".{ext}")

    def test_get_path_directory(self, mock_config):
        """Testa geração de caminho de diretório"""
        result = get_path_directory(mock_config.vdsc.dir_tmp, "video123")
        assert result == "/tmp/video123/"

    def test_get_path_directory_formats_correctly(self):
        """Testa que get_path_directory formata o caminho corretamente"""
        path = get_path_directory("output", "video123")
        assert path == "output/video123/"

    def test_get_multiplier_time_unit_seconds(self):
        """Testa multiplicador para segundos"""
        result = get_multiplier_time_unit("s")
        assert result == 1000

    def test_get_multiplier_time_unit_milliseconds(self):
        """Testa multiplicador para milissegundos"""
        result = get_multiplier_time_unit("ms")
        assert result == 1

    def test_get_multiplier_time_unit_other_units(self):
        """Testa multiplicador para outras unidades retorna 1"""
        multiplier = get_multiplier_time_unit("m")
        assert multiplier == 1

        multiplier = get_multiplier_time_unit("h")
        assert multiplier == 1


    def test_metadata_update_status(self, valid_event_dto):
        """Testa atualização de status de metadados"""
        metadata = VdscMetadata(dto=valid_event_dto)
        log = LogEntry("Teste de log")

        result = metadata_update_status(metadata, VdscStatusEnum.PROCESSING, log)

        assert result.status == VdscStatusEnum.PROCESSING.value
        assert len(result.logs) == 1

    def test_create_temporary_file(self):
        """Testa criação de arquivo temporário"""
        video_data = b"fake_video_data"

        result = create_temporary_file(video_data, "mp4")

        assert result.endswith(".mp4")
        import os
        assert os.path.exists(result)
        os.remove(result)

    def test_create_temporary_file_with_valid_data(self):
        """Testa criação de arquivo temporário com dados válidos"""
        test_data = b"test video data"
        file_path = create_temporary_file(test_data, "mp4")

        assert file_path is not None
        assert file_path.endswith(".mp4")

        # Verifica se o arquivo foi criado
        import os
        assert os.path.exists(file_path)

        # Limpa o arquivo
        os.remove(file_path)

    def test_create_temporary_file_preserves_data(self):
        """Testa que create_temporary_file preserva os dados"""
        test_data = b"important video content"
        file_path = create_temporary_file(test_data, "avi")

        # Lê o arquivo e verifica o conteúdo
        with open(file_path, 'rb') as f:
            content = f.read()

        assert content == test_data

        # Limpa
        import os
        os.remove(file_path)

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
        from unittest.mock import patch
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

        # Mock do cv2.resize para retornar o resultado esperado
        with patch('core.utils.slice_video_process_frame_util.cv2.resize') as mock_resize:
            mock_resize.return_value = np.zeros((720, 1280, 3), dtype=np.uint8)
            result = frame_resize(frame, 1280, 720)
            assert result.shape == (720, 1280, 3)

    def test_encode_frame_to_jpg(self):
        """Testa codificação de frame para JPG"""
        import numpy as np
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)

        result = encode_frame_to_jpg(frame, 95)

        assert result is not None

    def test_create_interval_list_recurrent(self, valid_event_dto):
        """Testa criação de lista de intervalos recorrentes"""
        valid_event_dto.interval_time = [5]
        valid_event_dto.start_time = 0
        valid_event_dto.end_time = 20
        metadata = VdscMetadata(dto=valid_event_dto)

        result = create_interval_list(metadata, 1000)

        assert result == [0, 5000, 10000, 15000, 20000]

    def test_create_interval_list_specific(self, valid_event_dto):
        """Testa criação de lista de intervalos específicos"""
        valid_event_dto.interval_time = [5, 10, 15]
        metadata = VdscMetadata(dto=valid_event_dto)

        result = create_interval_list(metadata, 1000)

        assert result == [5000, 10000, 15000]


    def test_set_exception_status_failed(self, mock_gateway, mock_config, valid_event_dto):
        """Testa definição de status FAILED"""
        metadata = VdscMetadata(dto=valid_event_dto)
        metadata.retries = 3
        metadata.max_retries = 3
        ex = Exception("Erro de teste")

        result_metadata, message = set_exception_status(mock_gateway, ex, metadata, VdscStatusEnum.FAILED, mock_config)

        assert result_metadata.status == VdscStatusEnum.FAILED.value
        assert "falhou após 3 tentativas" in message
        assert not mock_gateway.send_schedule_retry_event.called

    def test_set_exception_status_retrying(self, mock_gateway, mock_config, valid_event_dto):
        """Testa definição de status RETRYING"""
        metadata = VdscMetadata(dto=valid_event_dto)
        metadata.retries = 1
        metadata.max_retries = 3
        ex = Exception("Erro de teste")

        result_metadata, message = set_exception_status(mock_gateway, ex, metadata, VdscStatusEnum.RETRYING, mock_config)

        assert result_metadata.status == VdscStatusEnum.RETRYING.value
        assert "Tentativa 2 de 3" in message
        assert mock_gateway.send_schedule_retry_event.called

    def test_set_exception_status_failed_direct(self, mock_gateway, mock_config, valid_event_dto):
        """Testa função set_exception_status_failed diretamente"""
        metadata = VdscMetadata(dto=valid_event_dto)
        metadata.max_retries = 3
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
        metadata.max_retries = 3
        ex = Exception("Erro temporário")

        result_metadata, message = set_exception_status(mock_gateway, ex, metadata, VdscStatusEnum.RETRYING, mock_config)

        assert result_metadata.status == VdscStatusEnum.RETRYING.value
        assert "Tentativa 1 de 3" in message
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
        """Testa criação de notificação sem conteúdo deve validar canal"""
        metadata = VdscMetadata(dto=valid_event_dto)

        # Canal EMAIL requer EmailPayload, então deve lançar exceção
        with pytest.raises(ValueError, match="Canal EMAIL requer EmailPayload"):
            create_notification(metadata, ['email'], None, None)

    def test_metadata_update_status_changes_status(self, valid_event_dto):
        """Testa que metadata_update_status muda o status"""
        metadata = VdscMetadata(dto=valid_event_dto)
        original_status = metadata.status

        log = LogEntry("Status alterado para PROCESSING")
        result = metadata_update_status(metadata, VdscStatusEnum.PROCESSING, log)

        assert result.status == VdscStatusEnum.PROCESSING.value
        assert result.status != original_status
        assert len(result.logs) > 0

    def test_metadata_update_status_adds_log(self, valid_event_dto):
        """Testa que metadata_update_status adiciona log"""
        metadata = VdscMetadata(dto=valid_event_dto)
        initial_logs = len(metadata.logs)

        log = LogEntry("Test log message")
        result = metadata_update_status(metadata, VdscStatusEnum.FINISHED, log)

        assert len(result.logs) == initial_logs + 1
        assert result.logs[-1].info == "Test log message"


    def test_get_frame_new_size_preserves_aspect_ratio(self):
        """Testa que get_frame_new_size preserva proporção"""
        import numpy as np
        # Cria um frame com proporção 16:9 (1920x1080)
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)

        # Solicita redimensionar para altura mínima de 720
        new_width, new_height = get_frame_new_size(frame, 720)

        # Verifica se a proporção foi mantida
        original_ratio = 1920 / 1080  # ~1.778
        new_ratio = new_width / new_height

        assert abs(original_ratio - new_ratio) < 0.01
        assert new_height == 720


    def test_create_interval_list_with_single_interval(self, valid_event_dto):
        """Testa criação de intervalo recorrente"""
        valid_event_dto.interval_time = [5]
        valid_event_dto.start_time = 0
        valid_event_dto.end_time = 15
        metadata = VdscMetadata(dto=valid_event_dto)

        result = create_interval_list(metadata, 1000)

        assert 0 in result
        assert 5000 in result
        assert 10000 in result
        assert 15000 in result

    def test_create_interval_list_with_multiple_intervals(self, valid_event_dto):
        """Testa criação com múltiplos intervalos específicos"""
        valid_event_dto.interval_time = [2, 4, 6]
        metadata = VdscMetadata(dto=valid_event_dto)

        result = create_interval_list(metadata, 1000)

        assert result == [2000, 4000, 6000]

    def test_get_recurrent_interval_times_basic(self):
        """Testa geração básica de intervalos recorrentes"""
        result = get_recurrent_interval_times(0, 10, 2)

        assert result == [0, 2, 4, 6, 8, 10]

    def test_get_recurrent_interval_times_with_offset(self):
        """Testa geração com offset de início"""
        result = get_recurrent_interval_times(100, 110, 2)

        assert result == [100, 102, 104, 106, 108, 110]

    def test_get_specific_interval_times_basic(self):
        """Testa conversão de intervalos específicos"""
        result = get_specific_interval_times([1, 2, 3], 1000)

        assert result == [1000, 2000, 3000]

    def test_get_specific_interval_times_with_strings(self):
        """Testa conversão com números como strings"""
        result = get_specific_interval_times(["1", "2", "3"], 1000)

        assert result == [1000, 2000, 3000]

    def test_metadata_update_status_preserves_other_fields(self, valid_event_dto):
        """Testa que update_status preserva outros campos"""
        metadata = VdscMetadata(dto=valid_event_dto)
        original_video_id = metadata.video_id
        original_file_name = metadata.file_name

        log = LogEntry("Nova tentativa")
        result = metadata_update_status(metadata, VdscStatusEnum.RETRYING, log)

        assert result.video_id == original_video_id
        assert result.file_name == original_file_name
        assert result.status == VdscStatusEnum.RETRYING.value

    def test_check_resizer_needed_landscape_format(self):
        """Testa redimensionamento para formato landscape"""
        from core.utils.slice_process_util import _check_resizer_needed
        import numpy as np
        import tempfile

        # Cria arquivo temporário
        test_data = b"fake"
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            temp_path = f.name
            f.write(test_data)

        try:
            with patch('core.utils.slice_process_util.cv2.VideoCapture') as mock_cap:
                mock_instance = MagicMock()
                mock_cap.return_value = mock_instance
                # Frame 1920x1080 (landscape)
                mock_instance.read.return_value = (True, np.zeros((1080, 1920, 3), dtype=np.uint8))

                result = _check_resizer_needed(720, temp_path)

                # Verifica que as dimensões foram redimensionadas mantendo proporção
                assert result["resize"] is True
                assert result["new_height"] == 720
                assert result["new_width"] > 720
        finally:
            import os
            os.remove(temp_path)

    def test_check_resizer_needed_portrait_format(self):
        """Testa redimensionamento para formato portrait"""
        from core.utils.slice_process_util import _check_resizer_needed
        import numpy as np
        import tempfile

        test_data = b"fake"
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            temp_path = f.name
            f.write(test_data)

        try:
            with patch('core.utils.slice_process_util.cv2.VideoCapture') as mock_cap:
                mock_instance = MagicMock()
                mock_cap.return_value = mock_instance
                # Frame 1080x1920 (portrait)
                mock_instance.read.return_value = (True, np.zeros((1920, 1080, 3), dtype=np.uint8))

                result = _check_resizer_needed(720, temp_path)

                assert result["resize"] is True
                assert result["new_width"] == 720
                assert result["new_height"] > 720
        finally:
            import os
            os.remove(temp_path)

    def test_print_schedule_brasil_boundary_times(self):
        """Testa conversão em horas limite"""
        from core.utils.slice_process_util import _print_schedule_brasil
        from datetime import datetime, timezone

        # Testa 3:00 UTC (deve ser 00:00 em Brasília)
        utc_time = datetime(2026, 2, 13, 3, 0, 0, tzinfo=timezone.utc)
        result = _print_schedule_brasil(utc_time)
        assert "13/02/2026 00:00" == result

        # Testa 23:00 UTC (deve ser 20:00 em Brasília)
        utc_time = datetime(2026, 2, 13, 23, 0, 0, tzinfo=timezone.utc)
        result = _print_schedule_brasil(utc_time)
        assert "13/02/2026 20:00" == result


    def test_create_temporary_file_different_extensions(self):
        """Testa criação com diferentes extensões"""
        import os

        extensions = ["avi", "mov", "mkv", "webm"]
        temp_files = []

        try:
            for ext in extensions:
                file_path = create_temporary_file(b"test_data", ext)
                temp_files.append(file_path)

                assert file_path.endswith(f".{ext}")
                assert os.path.exists(file_path)

                # Verifica conteúdo
                with open(file_path, 'rb') as f:
                    assert f.read() == b"test_data"
        finally:
            for f in temp_files:
                if os.path.exists(f):
                    os.remove(f)

    def test_get_frame_new_size_with_small_target(self):
        """Testa redimensionamento com alvo pequeno"""
        import numpy as np

        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        new_width, new_height = get_frame_new_size(frame, 360)

        # Verifica que foi redimensionado para tamanho bem menor
        assert new_height == 360
        assert new_width < 1920

    def test_get_frame_new_size_with_large_target(self):
        """Testa redimensionamento com alvo grande"""
        import numpy as np

        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        new_width, new_height = get_frame_new_size(frame, 2160)

        # Verifica proporcionalidade
        original_ratio = 1920 / 1080
        new_ratio = new_width / new_height

        assert abs(original_ratio - new_ratio) < 0.01

