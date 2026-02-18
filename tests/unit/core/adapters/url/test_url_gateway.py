"""Testes unitários para UrlGateway"""
import pytest
from unittest.mock import Mock
from core.adapters.url.url_gateway import UrlGateway
from core.dtos.url_dto import UrlRequestDto, UrlResponseDto
from core.domain.url import Url


@pytest.mark.unit
class TestUrlGateway:
    """Testes para a classe UrlGateway"""

    @pytest.fixture
    def mock_datasource(self):
        """Fixture com datasource mockado"""
        datasource = Mock()
        datasource.generate_presigned_url = Mock()
        return datasource

    @pytest.fixture
    def gateway(self, mock_datasource):
        """Fixture com gateway"""
        return UrlGateway(mock_datasource)

    @pytest.fixture
    def valid_request_dto(self):
        """Fixture com UrlRequestDto válido"""
        return UrlRequestDto(
            file_name="test_video.mp4",
            action="upload")

    def test_gateway_init(self, mock_datasource):
        """Testa inicialização do gateway"""
        gateway = UrlGateway(mock_datasource)

        assert gateway.datasource == mock_datasource

    def test_generate_presigned_url_calls_datasource(self, gateway, mock_datasource, valid_request_dto):
        """Testa que generate_presigned_url chama o datasource"""
        mock_datasource.generate_upload_presigned_url.return_value = UrlResponseDto(
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/url"
        )

        url = Url.from_request(valid_request_dto)
        result = gateway.generate_upload_presigned_url(url)

        assert mock_datasource.generate_upload_presigned_url.called

    def test_generate_presigned_url_returns_url(self, gateway, mock_datasource, valid_request_dto):
        """Testa que generate_presigned_url retorna Url"""
        mock_datasource.generate_upload_presigned_url.return_value = UrlResponseDto(
            url_endpoint="https://s3.amazonaws.com/url",
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            fields=None
        )

        url = Url.from_request(valid_request_dto)
        result = gateway.generate_upload_presigned_url(url)

        assert isinstance(result, Url)
        assert result.file_name == "test_video.mp4"
        assert result.url_endpoint == "https://s3.amazonaws.com/url"

    def test_generate_presigned_url_with_upload_operation(self, gateway, mock_datasource):
        """Testa geração de URL para operação de upload"""
        request_dto = UrlRequestDto(
            file_name="video.mp4",
            action="upload"
        )

        mock_datasource.generate_upload_presigned_url.return_value = UrlResponseDto(
            url_endpoint="https://s3.amazonaws.com/upload-url",
            file_name="video.mp4",
            action="upload",
            method="POST",
            fields=None
        )

        url = Url.from_request(request_dto)
        result = gateway.generate_upload_presigned_url(url)

        assert result.action == "upload"

    def test_generate_presigned_url_with_download_operation(self, gateway, mock_datasource):
        """Testa geração de URL para operação de download"""
        request_dto = UrlRequestDto(
            file_name="video.mp4",
            action="download"
        )

        mock_datasource.generate_download_presigned_url.return_value = UrlResponseDto(
            url_endpoint="https://s3.amazonaws.com/download-url",
            file_name="video.mp4",
            action="download",
            method="GET",
            fields=None
        )

        url = Url.from_request(request_dto)
        result = gateway.generate_download_presigned_url(url)

        assert result.action == "download"

    def test_generate_presigned_url_preserves_filename(self, gateway, mock_datasource):
        """Testa que o nome do arquivo é preservado"""
        request_dto = UrlRequestDto(
            file_name="my_important_file.mp4",
            action="upload"
        )

        mock_datasource.generate_upload_presigned_url.return_value = UrlResponseDto(
            url_endpoint="https://s3.amazonaws.com/url",
            file_name="my_important_file.mp4",
            action="upload",
            method="POST",
            fields=None
        )

        url = Url.from_request(request_dto)
        result = gateway.generate_upload_presigned_url(url)

        assert result.file_name == "my_important_file.mp4"

    def test_generate_presigned_url_with_fields(self, gateway, mock_datasource, valid_request_dto):
        """Testa geração de URL com fields"""
        fields = {
            "key": "uploads/test_video.mp4",
            "bucket": "my-bucket",
            "acl": "private"
        }

        mock_datasource.generate_upload_presigned_url.return_value = UrlResponseDto(
            url_endpoint="https://s3.amazonaws.com/url",
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            fields=fields
        )

        url = Url.from_request(valid_request_dto)
        result = gateway.generate_upload_presigned_url(url)

        assert result.fields == fields

    def test_gateway_handles_different_file_types(self, gateway, mock_datasource):
        """Testa gateway com diferentes tipos de arquivo"""
        file_types = [
            ("video.mp4", "video/mp4"),
            ("image.jpg", "image/jpeg"),
            ("document.pdf", "application/pdf")
        ]

        for file_name, content_type in file_types:
            request_dto = UrlRequestDto(
                file_name=file_name,
                action="upload"
            )

            mock_datasource.generate_upload_presigned_url.return_value = UrlResponseDto(
                url_endpoint="https://s3.amazonaws.com/url",
                file_name=file_name,
                action="upload",
                method="POST",
                fields=None
            )

            url = Url.from_request(request_dto)
            result = gateway.generate_upload_presigned_url(url)

            assert result.file_name == file_name
