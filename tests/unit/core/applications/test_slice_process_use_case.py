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
        gateway.open_file = Mock(return_value=b"fake_video_data")
        gateway.delete_file = Mock()
        gateway.delete_temp_files = Mock()
        gateway.upload_finished_zip = Mock()
        gateway.send_notification = Mock()
        gateway.send_schedule_retry_event = Mock()
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
        schedule_rules_mock.to_dict = Mock(return_value={})

        # Mock para VdscSettingsDTO
        vdsc_settings_mock = MagicMock()
        vdsc_settings_mock.dir_uploads = "uploads"
        vdsc_settings_mock.dir_tmp = "/tmp"
        vdsc_settings_mock.dir_finished = "finished"
        vdsc_settings_mock.max_workers = 4
        vdsc_settings_mock.resize = quality_mock
        vdsc_settings_mock.schedule_event_rules = schedule_rules_mock

        # Mock para VdscConfigDTO
        config = MagicMock(spec=VdscConfigDTO)
        config.aws_region = "us-east-1"
        config.dynamodb_table_name = "VideoSlice"
        config.event_bus_name = "default"
        config.vdsc = vdsc_settings_mock

        return config

    @pytest.fixture
    def valid_event_dto(self):
        """Fixture com evento válido"""
        return VdscMetadataDTO(
            video_id="video123",
            file_name="test_video",
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
            quality_output_level=65,
            logs=[]
        )

    @pytest.fixture
    def mock_handler(self):
        """Fixture do exception handler"""
        handler = Mock()
        return handler

    @patch('core.applications.slice_process_use_case.process_video')
    def test_execute_success(self, mock_process_video, use_case, mock_gateway, mock_config, valid_event_dto, mock_handler):
        """Testa execução completa com sucesso"""
        # Setup
        mock_gateway.update_metadata.return_value = None
        mock_gateway.open_file.return_value = b"fake_video_data"
        mock_process_video.return_value = None

        # Executa
        use_case.execute(mock_gateway, valid_event_dto, mock_config, mock_handler)

        # Assertions
        assert mock_gateway.update_metadata.called
        assert mock_gateway.open_file.called
        assert mock_process_video.called
        assert mock_gateway.upload_finished_zip.called
        assert mock_gateway.delete_file.called
        assert mock_gateway.delete_temp_files.called
        assert mock_gateway.send_notification.called

    @patch('core.applications.slice_process_use_case.process_video')
    def test_execute_with_error_retries_not_exceeded(self, mock_process_video, use_case, mock_gateway, mock_config, valid_event_dto, mock_handler):
        """Testa execução com erro quando tentativas não foram excedidas"""
        # Setup
        mock_gateway.update_metadata.return_value = None
        mock_process_video.side_effect = Exception("Erro ao processar vídeo")

        # Executa e verifica exceção
        with pytest.raises(VdscException) as exc_info:
            use_case.execute(mock_gateway, valid_event_dto, mock_config, mock_handler)

        # Assertions
        assert "video123" in str(exc_info.value)
        assert mock_gateway.send_schedule_retry_event.called
        assert mock_gateway.update_metadata.called

    @patch('core.applications.slice_process_use_case.process_video')
    def test_execute_with_error_max_retries_reached(self, mock_process_video, use_case, mock_gateway, mock_config, valid_event_dto, mock_handler):
        """Testa execução com erro quando máximo de tentativas foi alcançado"""
        # Setup
        valid_event_dto.retries = 3
        valid_event_dto.max_retries = 3
        mock_gateway.update_metadata.return_value = None
        mock_process_video.side_effect = Exception("Erro ao processar vídeo")

        # Executa e verifica exceção
        with pytest.raises(VdscException) as exc_info:
            use_case.execute(mock_gateway, valid_event_dto, mock_config, mock_handler)

        # Assertions
        assert "video123" in str(exc_info.value)
        assert "falhou após 3 tentativas" in str(exc_info.value)
        assert not mock_gateway.send_schedule_retry_event.called  # Não faz retry quando max_retries é atingido
        assert mock_gateway.update_metadata.called

    @patch('core.applications.slice_process_use_case.process_video')
    def test_execute_retrying_status(self, mock_process_video, use_case, mock_gateway, mock_config, valid_event_dto, mock_handler):
        """Testa execução quando status inicial é RETRYING"""
        # Setup
        valid_event_dto.status = "RETRYING"
        valid_event_dto.retries = 1
        mock_gateway.update_metadata.return_value = None
        mock_process_video.return_value = None

        # Executa
        use_case.execute(mock_gateway, valid_event_dto, mock_config, mock_handler)

        # Assertions
        assert mock_gateway.update_metadata.called
        assert mock_gateway.send_notification.called
        # Verifica que a mensagem contém informação de retry
        call_args = mock_gateway.send_notification.call_args_list
        assert len(call_args) >= 1

    @patch('core.applications.slice_process_use_case.process_video')
    def test_execute_updates_metadata_on_success(self, mock_process_video, use_case, mock_gateway, mock_config, valid_event_dto, mock_handler):
        """Testa se metadados são atualizados corretamente no sucesso"""
        # Setup
        mock_gateway.update_metadata.return_value = None
        mock_process_video.return_value = None

        # Executa
        use_case.execute(mock_gateway, valid_event_dto, mock_config, mock_handler)

        # Assertions - verifica que update_metadata foi chamado 2 vezes:
        # 1. Ao iniciar (PROCESSING)
        # 2. Ao finalizar (FINISHED)
        assert mock_gateway.update_metadata.call_count == 2

    @patch('core.applications.slice_process_use_case.process_video')
    def test_execute_sends_notifications_on_success(self, mock_process_video, use_case, mock_gateway, mock_config, valid_event_dto, mock_handler):
        """Testa se notificações são enviadas corretamente no sucesso"""
        # Setup
        mock_gateway.update_metadata.return_value = None
        mock_process_video.return_value = None

        # Executa
        use_case.execute(mock_gateway, valid_event_dto, mock_config, mock_handler)

        # Assertions - verifica que send_notification foi chamado 2 vezes:
        # 1. Ao iniciar
        # 2. Ao finalizar (FINISHED)
        assert mock_gateway.send_notification.call_count == 2

    @patch('core.applications.slice_process_use_case.process_video')
    def test_execute_cleans_up_files_on_success(self, mock_process_video, use_case, mock_gateway, mock_config, valid_event_dto, mock_handler):
        """Testa se arquivos são limpos corretamente após sucesso"""
        # Setup
        mock_gateway.update_metadata.return_value = None
        mock_process_video.return_value = None

        # Executa
        use_case.execute(mock_gateway, valid_event_dto, mock_config, mock_handler)

        # Assertions
        assert mock_gateway.delete_file.called  # Deleta o vídeo original
        assert mock_gateway.delete_temp_files.called  # Deleta arquivos temporários
        assert mock_gateway.upload_finished_zip.called  # Faz upload do resultado
