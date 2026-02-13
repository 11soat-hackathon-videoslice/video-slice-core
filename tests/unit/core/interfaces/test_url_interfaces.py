"""Testes para as interfaces de URL"""
import pytest
from unittest.mock import MagicMock

from core.interfaces.url.url_interfaces import (
    UrlGatewayInterface,
    UrlDataSourceInterface,
    UrlControllerInterface
)
from core.domain import Url
from core.dtos import UrlRequestDto, UrlResponseDto


@pytest.mark.unit
class TestUrlGatewayInterface:
    """Testes para UrlGatewayInterface"""

    def test_interface_is_abstract(self):
        """Testa que a interface é abstrata"""
        with pytest.raises(TypeError):
            UrlGatewayInterface()

    def test_interface_has_required_methods(self):
        """Testa que a interface tem os métodos necessários"""
        required_methods = [
            'generate_download_presigned_url',
            'generate_upload_presigned_url'
        ]

        for method in required_methods:
            assert hasattr(UrlGatewayInterface, method)

    def test_concrete_implementation_gateway(self):
        """Testa implementação concreta do gateway"""

        class ConcreteUrlGateway(UrlGatewayInterface):
            def generate_download_presigned_url(self, url: Url) -> Url:
                url.presigned_url = f"https://example.com/download/{url.key}"
                return url

            def generate_upload_presigned_url(self, url: Url) -> Url:
                url.presigned_url = f"https://example.com/upload/{url.key}"
                return url

        gateway = ConcreteUrlGateway()

        # Testa download URL
        url_download = MagicMock(spec=Url)
        url_download.key = "test-video.mp4"
        result = gateway.generate_download_presigned_url(url_download)
        assert result.presigned_url == "https://example.com/download/test-video.mp4"

        # Testa upload URL
        url_upload = MagicMock(spec=Url)
        url_upload.key = "test-video.mp4"
        result = gateway.generate_upload_presigned_url(url_upload)
        assert result.presigned_url == "https://example.com/upload/test-video.mp4"


@pytest.mark.unit
class TestUrlDataSourceInterface:
    """Testes para UrlDataSourceInterface"""

    def test_interface_is_abstract(self):
        """Testa que a interface é abstrata"""
        with pytest.raises(TypeError):
            UrlDataSourceInterface()

    def test_interface_has_required_methods(self):
        """Testa que a interface tem os métodos necessários"""
        required_methods = [
            'generate_download_presigned_url',
            'generate_upload_presigned_url'
        ]

        for method in required_methods:
            assert hasattr(UrlDataSourceInterface, method)

    def test_concrete_implementation_datasource(self):
        """Testa implementação concreta do datasource"""

        class ConcreteUrlDataSource(UrlDataSourceInterface):
            def generate_download_presigned_url(self, url: UrlRequestDto) -> UrlResponseDto:
                return UrlResponseDto(
                    url_endpoint=f"https://s3.amazonaws.com/download/{url.file_name}",
                    file_name=url.file_name,
                    action="download",
                    method="GET"
                )

            def generate_upload_presigned_url(self, url: UrlRequestDto) -> UrlResponseDto:
                return UrlResponseDto(
                    url_endpoint=f"https://s3.amazonaws.com/upload/{url.file_name}",
                    file_name=url.file_name,
                    action="upload",
                    method="PUT"
                )

        datasource = ConcreteUrlDataSource()

        # Testa download
        request = UrlRequestDto(
            file_name="video.mp4",
            action="download"
        )
        response = datasource.generate_download_presigned_url(request)
        assert response.file_name == "video.mp4"
        assert "download" in response.url_endpoint

        # Testa upload
        response = datasource.generate_upload_presigned_url(request)
        assert response.file_name == "video.mp4"
        assert "upload" in response.url_endpoint


@pytest.mark.unit
class TestUrlControllerInterface:
    """Testes para UrlControllerInterface"""

    def test_interface_is_abstract(self):
        """Testa que a interface é abstrata"""
        with pytest.raises(TypeError):
            UrlControllerInterface()

    def test_interface_has_generate_presigned_url_method(self):
        """Testa que a interface tem o método generate_presigned_url"""
        assert hasattr(UrlControllerInterface, 'generate_presigned_url')

    def test_concrete_implementation_controller(self):
        """Testa implementação concreta do controller"""

        class ConcreteUrlController(UrlControllerInterface):
            def generate_presigned_url(self, request: UrlRequestDto) -> dict:
                return {
                    "file_name": request.file_name,
                    "url": f"https://s3.amazonaws.com/{request.file_name}",
                    "expires_in": 3600,
                    "status": "success"
                }

        controller = ConcreteUrlController()

        request = UrlRequestDto(
            file_name="test.mp4",
            action="download"
        )

        response = controller.generate_presigned_url(request)

        assert response["status"] == "success"
        assert response["file_name"] == "test.mp4"
        assert response["expires_in"] == 3600
        assert "https" in response["url"]

