"""Testes unitários para slice_video_process_frame_util"""
from unittest.mock import MagicMock, patch

import pytest
import sys

# Mock cv2 with proper constants
cv2_mock = MagicMock()
cv2_mock.CAP_PROP_POS_MSEC = 0
cv2_mock.IMWRITE_JPEG_QUALITY = 6
cv2_mock.INTER_AREA = 1
sys.modules['cv2'] = cv2_mock

from core.utils.slice_video_process_frame_util import (
    process_video_frame,
    encode_frame_to_jpg,
    frame_resize,
    get_frame_size
)
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO
from core.domain.vdsc_metadata import VdscMetadata


@pytest.mark.unit
class TestSliceVideoProcessFrameUtil:
    """Testes para as funções utilitárias de processamento de frames de vídeo"""

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
            quality_output_level=80,
            logs=[]
        )

    @patch('core.utils.slice_video_process_frame_util.cv2.VideoCapture')
    @patch('core.utils.slice_video_process_frame_util.cv2.imencode')
    @patch('core.utils.slice_video_process_frame_util.cv2.resize')
    def test_process_video_frame_success_with_resize(self, mock_cv2_resize, mock_imencode, mock_video_capture, valid_event_dto):
        """Testa processamento de um frame com sucesso e redimensionamento"""
        import numpy as np

        # Setup
        metadata = VdscMetadata(dto=valid_event_dto)
        resize_params = {'resize': True, 'new_width': 1280, 'new_height': 720}

        # Mock do video capture
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, mock_frame)

        # Mock do resize
        resized_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        mock_cv2_resize.return_value = resized_frame

        # Mock do imencode
        mock_imencode.return_value = (True, np.array([255, 216, 255], dtype=np.uint8))

        # Executa
        result = process_video_frame(
            1000, "test_video.mp4", resize_params, metadata,
            "processing/video123/", "high", "video123", 1000
        )

        # Assertions
        assert result is not None
        assert result['success'] is True
        assert result['file_output'] == "processing/video123/video123_high_1_s.jpg"
        assert result['data'] is not None
        # Verifica que set foi chamado com tempo em ms
        mock_cap.set.assert_called_once()
        assert mock_cap.set.call_args[0][1] == 1000
        mock_video_capture.assert_called_once_with("test_video.mp4")
        mock_cap.release.assert_called_once()
        # Verifica que resize foi chamado
        assert mock_cv2_resize.called

    @patch('core.utils.slice_video_process_frame_util.cv2.VideoCapture')
    @patch('core.utils.slice_video_process_frame_util.cv2.imencode')
    def test_process_video_frame_success_without_resize(self, mock_imencode, mock_video_capture, valid_event_dto):
        """Testa processamento de um frame com sucesso sem redimensionamento"""
        import numpy as np

        # Setup
        metadata = VdscMetadata(dto=valid_event_dto)
        resize_params = {'resize': False, 'new_width': None, 'new_height': None}

        # Mock do video capture
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, mock_frame)
        mock_cap.set = MagicMock()

        # Mock do imencode
        mock_imencode.return_value = (True, np.array([255, 216, 255], dtype=np.uint8))

        # Executa
        result = process_video_frame(
            2000, "test_video.mp4", resize_params, metadata,
            "processing/video123/", "medium", "video123", 1000
        )

        # Assertions
        assert result is not None
        assert result['success'] is True
        assert result['file_output'] == "processing/video123/video123_medium_2_s.jpg"
        assert result['data'] is not None
        mock_cap.release.assert_called_once()

    @patch('core.utils.slice_video_process_frame_util.cv2.VideoCapture')
    def test_process_video_frame_failure_read_frame(self, mock_video_capture, valid_event_dto):
        """Testa processamento de um frame com falha na leitura"""
        # Setup
        metadata = VdscMetadata(dto=valid_event_dto)
        resize_params = {'resize': False, 'new_width': None, 'new_height': None}

        # Mock do video capture com falha
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_cap.read.return_value = (False, None)
        mock_cap.set = MagicMock()

        # Executa
        result = process_video_frame(
            1000, "test_video.mp4", resize_params, metadata,
            "processing/video123/", "high", "video123", 1000
        )

        # Assertions - retorna None quando falha na leitura
        assert result is None
        mock_cap.release.assert_called_once()

    @patch('core.utils.slice_video_process_frame_util.cv2.VideoCapture')
    def test_process_video_frame_failure_frame_is_none(self, mock_video_capture, valid_event_dto):
        """Testa processamento quando frame é None mesmo com sucesso"""
        # Setup
        metadata = VdscMetadata(dto=valid_event_dto)
        resize_params = {'resize': False, 'new_width': None, 'new_height': None}

        # Mock do video capture - sucesso mas frame é None
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_cap.read.return_value = (True, None)
        mock_cap.set = MagicMock()

        # Executa
        result = process_video_frame(
            1000, "test_video.mp4", resize_params, metadata,
            "processing/video123/", "high", "video123", 1000
        )

        # Assertions - retorna None quando frame é None
        assert result is None
        mock_cap.release.assert_called_once()

    @patch('core.utils.slice_video_process_frame_util.cv2.VideoCapture')
    @patch('core.utils.slice_video_process_frame_util.cv2.imencode')
    def test_process_video_frame_encode_failure(self, mock_imencode, mock_video_capture, valid_event_dto):
        """Testa processamento quando imencode falha"""
        import numpy as np

        # Setup
        metadata = VdscMetadata(dto=valid_event_dto)
        resize_params = {'resize': False, 'new_width': None, 'new_height': None}

        # Mock do video capture
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        mock_cap.read.return_value = (True, mock_frame)
        mock_cap.set = MagicMock()

        # Mock do imencode com falha
        mock_imencode.return_value = (False, None)

        # Executa
        result = process_video_frame(
            1000, "test_video.mp4", resize_params, metadata,
            "processing/video123/", "high", "video123", 1000
        )

        # Assertions
        assert result is not None
        assert result['success'] is False
        assert result['data'] is None
        mock_cap.release.assert_called_once()

    @patch('core.utils.slice_video_process_frame_util.cv2.VideoCapture')
    def test_process_video_frame_exception_handling(self, mock_video_capture, valid_event_dto):
        """Testa que exceções são tratadas e liberam recursos"""
        # Setup
        metadata = VdscMetadata(dto=valid_event_dto)
        resize_params = {'resize': False, 'new_width': None, 'new_height': None}

        # Mock do video capture lançando exceção
        mock_cap = MagicMock()
        mock_video_capture.return_value = mock_cap
        mock_cap.set.side_effect = Exception("Erro ao configurar posição")

        # Executa
        with pytest.raises(Exception, match="Erro ao configurar posição"):
            process_video_frame(
                1000, "test_video.mp4", resize_params, metadata,
                "processing/video123/", "high", "video123", 1000
            )

        # Assertions - verifica que release foi chamado mesmo com exceção (finally)
        mock_cap.release.assert_called_once()

    def test_process_video_frame_time_unit_multiplier(self):
        """Testa que o multiplicador de tempo é aplicado corretamente"""
        import numpy as np

        with patch('core.utils.slice_video_process_frame_util.cv2.VideoCapture') as mock_video_capture, \
             patch('core.utils.slice_video_process_frame_util.cv2.imencode') as mock_imencode:

            dto = VdscMetadataDTO(
                video_id="video456",
                file_name="test.mp4",
                file_extension="mp4",
                status="UPLOADED",
                created="2026-01-13T00:00:00Z",
                user_id="user123",
                total_time=3600,
                unit_time="ms",  # millisegundos
                start_time=0,
                end_time=60,
                interval_time=[10],
                max_retries=3,
                retries=0,
                resize="high",
                quality_output_level=75,
                logs=[]
            )
            metadata = VdscMetadata(dto=dto)
            resize_params = {'resize': False, 'new_width': None, 'new_height': None}

            # Mock do video capture
            mock_cap = MagicMock()
            mock_video_capture.return_value = mock_cap
            mock_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
            mock_cap.read.return_value = (True, mock_frame)
            mock_cap.set = MagicMock()

            # Mock do imencode
            mock_imencode.return_value = (True, np.array([255, 216, 255], dtype=np.uint8))

            # Executa com time_unit_multiplier = 1
            result = process_video_frame(
                5000, "test.mp4", resize_params, metadata,
                "processing/video456/", "high", "video456", 1  # multiplicador = 1
            )

            # Assertions - suffix deve ser 5000 com unit_time "ms"
            assert result is not None
            assert "video456_high_5000_ms.jpg" in result['file_output']

    @patch('core.utils.slice_video_process_frame_util.cv2.imencode')
    def test_encode_frame_to_jpg(self, mock_imencode):
        """Testa codificação de frame para JPG"""
        import numpy as np

        # Setup
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        quality_level = 95

        # Mock do imencode
        encoded_data = np.array([255, 216, 255, 224], dtype=np.uint8)
        mock_imencode.return_value = (True, encoded_data)

        # Executa
        result = encode_frame_to_jpg(frame, quality_level)

        # Assertions
        assert result is not None
        success, data = result
        assert success is True
        assert data is encoded_data
        # Verifica que imencode foi chamado com os parâmetros corretos
        mock_imencode.assert_called_once()
        call_args = mock_imencode.call_args[0]
        assert call_args[0] == '.jpg'
        assert call_args[2][1] == 95  # quality_level

    @patch('core.utils.slice_video_process_frame_util.cv2.imencode')
    def test_encode_frame_to_jpg_failure(self, mock_imencode):
        """Testa codificação com falha"""
        import numpy as np

        # Setup
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)

        # Mock do imencode com falha
        mock_imencode.return_value = (False, None)

        # Executa
        result = encode_frame_to_jpg(frame, 95)

        # Assertions
        assert result is not None
        success, data = result
        assert success is False
        assert data is None

    @patch('core.utils.slice_video_process_frame_util.cv2.imencode')
    def test_encode_frame_to_jpg_different_quality_levels(self, mock_imencode):
        """Testa codificação com diferentes níveis de qualidade"""
        import numpy as np

        # Setup
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        mock_imencode.return_value = (True, np.array([255, 216, 255], dtype=np.uint8))

        # Testa diferentes níveis de qualidade
        for quality in [50, 75, 90, 100]:
            encode_frame_to_jpg(frame, quality)

        # Assertions - verifica que diferentes níveis foram passados
        assert mock_imencode.call_count == 4
        calls = mock_imencode.call_args_list
        assert calls[0][0][2][1] == 50
        assert calls[1][0][2][1] == 75
        assert calls[2][0][2][1] == 90
        assert calls[3][0][2][1] == 100

    @patch('core.utils.slice_video_process_frame_util.cv2.resize')
    def test_frame_resize(self, mock_cv2_resize):
        """Testa redimensionamento de frame"""
        import numpy as np

        # Setup
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        target_width = 1280
        target_height = 720

        # Mock do cv2.resize
        resized_frame = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        mock_cv2_resize.return_value = resized_frame

        # Executa
        result = frame_resize(frame, target_width, target_height)

        # Assertions
        assert result.shape == (target_height, target_width, 3)
        # Verifica que resize foi chamado com os parâmetros corretos
        mock_cv2_resize.assert_called_once()
        call_args = mock_cv2_resize.call_args[0]
        # Verifica que foi chamado com o frame e as dimensões corretas
        assert call_args[1] == (target_width, target_height)

    @patch('core.utils.slice_video_process_frame_util.cv2.resize')
    def test_frame_resize_different_dimensions(self, mock_cv2_resize):
        """Testa redimensionamento com diferentes dimensões"""
        import numpy as np

        # Setup
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        mock_cv2_resize.return_value = np.zeros((480, 854, 3), dtype=np.uint8)

        # Executa
        result = frame_resize(frame, 854, 480)

        # Assertions
        assert result.shape == (480, 854, 3)
        mock_cv2_resize.assert_called_once()

    def test_get_frame_size_no_resize_needed(self):
        """Testa quando frame já está no tamanho correto"""
        import numpy as np

        # Setup
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        target_height = 1080

        # Executa
        result = get_frame_size(frame, target_height)

        # Assertions - deve retornar o frame original pois altura <= target_height
        assert result is frame

    def test_get_frame_size_resize_needed(self):
        """Testa quando é necessário redimensionar"""
        import numpy as np

        # Setup
        frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        target_height = 720

        # Executa
        result = get_frame_size(frame, target_height)

        # Assertions - calcula nova largura mantendo proporção
        # ratio = 720 / 1080 = 0.667
        # new_width = 1920 * 0.667 = 1280
        assert result == (720, 1280)

    def test_get_frame_size_portrait_orientation(self):
        """Testa redimensionamento em orientação portrait"""
        import numpy as np

        # Setup - frame em portrait (altura > largura)
        frame = np.zeros((1920, 1080, 3), dtype=np.uint8)
        target_height = 720

        # Executa
        result = get_frame_size(frame, target_height)

        # Assertions
        # ratio = 720 / 1920 = 0.375
        # new_width = 1080 * 0.375 = 405
        assert result == (720, 405)

    def test_get_frame_size_small_height(self):
        """Testa quando altura do frame é menor que target_height"""
        import numpy as np

        # Setup
        frame = np.zeros((480, 854, 3), dtype=np.uint8)
        target_height = 720

        # Executa
        result = get_frame_size(frame, target_height)

        # Assertions - retorna o frame original
        assert result is frame

    def test_get_frame_size_exact_height(self):
        """Testa quando altura do frame é exatamente igual a target_height"""
        import numpy as np

        # Setup
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        target_height = 720

        # Executa
        result = get_frame_size(frame, target_height)

        # Assertions - retorna o frame original
        assert result is frame

