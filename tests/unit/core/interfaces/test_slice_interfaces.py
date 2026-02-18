"""Testes para as interfaces de Slice"""
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from core.domain.vdsc_metadata import VdscMetadata
from core.dtos.vdsc_config_dto import VdscConfigDTO
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO
from core.interfaces.slice.slice_controller_interface import SliceControllerInterface
from core.interfaces.slice.slice_dataproxy_interface import SliceDataProxyInterface
from core.interfaces.slice.slice_gateway_interface import SliceGatewayInferface


@pytest.mark.unit
class TestSliceControllerInterface:
    """Testes para SliceControllerInterface"""

    def test_interface_is_abstract(self):
        """Testa que a interface é abstrata e não pode ser instanciada"""
        with pytest.raises(TypeError):
            SliceControllerInterface()

    def test_interface_has_video_slice_processing_method(self):
        """Testa que a interface tem o método video_slice_processing"""
        assert hasattr(SliceControllerInterface, 'video_slice_processing')

    def test_concrete_implementation_must_implement_video_slice_processing(self):
        """Testa que implementação concreta deve ter video_slice_processing"""

        class ConcreteSliceController(SliceControllerInterface):
            def video_slice_processing(self, event: VdscMetadataDTO, config: VdscConfigDTO) -> dict:
                return {"status": "success"}

        controller = ConcreteSliceController()
        dto = VdscMetadataDTO(
            video_id="test",
            file_name="test.mp4",
            file_extension="mp4",
            status="uploaded",
            created="2026-01-13T00:00:00Z",
            user_id="user",
            total_time=100,
            unit_time="s",
            start_time=0,
            end_time=10,
            interval_time=["0"],
            max_retries=3,
            retries=0,
            resize="high",
            quality_output_level=50,
            logs=[]
        )
        config = MagicMock(spec=VdscConfigDTO)

        result = controller.video_slice_processing(dto, config)
        assert result["status"] == "success"


@pytest.mark.unit
class TestSliceDataProxyInterface:
    """Testes para SliceDataProxyInterface"""

    def test_interface_is_abstract(self):
        """Testa que a interface é abstrata"""
        with pytest.raises(TypeError):
            SliceDataProxyInterface()

    def test_interface_has_required_methods(self):
        """Testa que a interface tem todos os métodos necessários"""
        required_methods = [
            'delete_file',
            'delete_temp_files',
            'open_file',
            'save_file',
            'send_notification',
            'send_schedule_retry_event',
            'upload_finished_zip',
            'update_metadata_by_video_id'
        ]

        for method in required_methods:
            assert hasattr(SliceDataProxyInterface, method)

    def test_concrete_implementation_dataproxy(self):
        """Testa implementação concreta do dataproxy"""

        class ConcreteDataProxy(SliceDataProxyInterface):
            def delete_file(self, file_path: str) -> None:
                pass

            def delete_temp_files(self, tmp_path: str) -> None:
                pass

            def open_file(self, file_path: str) -> bytes:
                return b"test_data"

            def save_file(self, file_path: str, data: bytes) -> None:
                pass

            def send_metric(self, metric_info: str) -> None:
                pass

            def send_notification(self, notification) -> None:
                pass

            def send_schedule_retry_event(self, vdsc_metadata, schedule_time, schedule_config) -> None:
                pass

            def upload_finished_zip(self, output_directory: str, target_path: str) -> None:
                pass

            def update_metadata_by_video_id(self, update_data):
                return update_data

        dataproxy = ConcreteDataProxy()

        # Testa open_file
        result = dataproxy.open_file("test_path")
        assert result == b"test_data"

        # Testa update_metadata_by_video_id
        test_dto = MagicMock(spec=VdscMetadataDTO)
        result = dataproxy.update_metadata_by_video_id(test_dto)
        assert result == test_dto


@pytest.mark.unit
class TestSliceGatewayInterface:
    """Testes para SliceGatewayInterface"""

    def test_interface_is_abstract(self):
        """Testa que a interface é abstrata"""
        with pytest.raises(TypeError):
            SliceGatewayInferface()

    def test_interface_has_required_methods(self):
        """Testa que a interface tem todos os métodos necessários"""
        required_methods = [
            'delete_file',
            'delete_temp_files',
            'open_file',
            'save_file',
            'send_schedule_retry_event',
            'send_notification',
            'upload_finished_zip',
            'update_metadata'
        ]

        for method in required_methods:
            assert hasattr(SliceGatewayInferface, method)

    def test_concrete_implementation_gateway(self):
        """Testa implementação concreta do gateway"""

        class ConcreteGateway(SliceGatewayInferface):
            def delete_file(self, file_path: str) -> None:
                pass

            def delete_temp_files(self, tmp_path: str) -> None:
                pass

            def open_file(self, file_path: str) -> bytes:
                return b"gateway_data"

            def save_file(self, file_path: str, data: bytes) -> None:
                pass

            def send_metric(self, metric_info: str) -> None:
                pass

            def send_schedule_retry_event(self, vdsc_metadata, schedule_time, schedule_config) -> None:
                pass

            def send_notification(self, notification) -> None:
                pass

            def upload_finished_zip(self, output_directory: str, target_path: str) -> None:
                pass

            def update_metadata(self, update_data):
                return update_data

        gateway = ConcreteGateway()

        # Testa open_file
        result = gateway.open_file("test_path")
        assert result == b"gateway_data"

        # Testa update_metadata
        test_metadata = MagicMock(spec=VdscMetadata)
        result = gateway.update_metadata(test_metadata)
        assert result == test_metadata

    def test_gateway_methods_with_datetime(self):
        """Testa que o gateway aceita datetime corretamente"""

        class ConcreteGateway(SliceGatewayInferface):
            def __init__(self):
                self.called_with = None

            def delete_file(self, file_path: str) -> None:
                pass

            def delete_temp_files(self, tmp_path: str) -> None:
                pass

            def open_file(self, file_path: str) -> bytes:
                return b""

            def save_file(self, file_path: str, data: bytes) -> None:
                pass

            def send_metric(self, metric_info: str) -> None:
                pass

            def send_schedule_retry_event(self, vdsc_metadata, schedule_time, schedule_config) -> None:
                self.called_with = (vdsc_metadata, schedule_time, schedule_config)

            def send_notification(self, notification) -> None:
                pass

            def upload_finished_zip(self, output_directory: str, target_path: str) -> None:
                pass

            def update_metadata(self, update_data):
                return update_data

        gateway = ConcreteGateway()
        metadata = MagicMock(spec=VdscMetadata)
        schedule_time = datetime.now()
        schedule_config = {"retry_arn": "test"}

        gateway.send_schedule_retry_event(metadata, schedule_time, schedule_config)

        assert gateway.called_with[0] == metadata
        assert gateway.called_with[1] == schedule_time
        assert gateway.called_with[2] == schedule_config

