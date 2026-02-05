"""Testes unitários para UrlController"""
import pytest
from unittest.mock import Mock, patch
from core.adapters.url.url_controller import UrlController
from core.adapters.url.url_gateway import UrlGateway
from core.adapters.url.url_presenter import UrlPresenter
from core.dtos.url_dto import UrlRequestDto
from core.domain.url import Url


@pytest.mark.unit
class TestUrlController:
    """Testes para a classe UrlController"""

    @pytest.fixture
    def mock_datasource(self):
        """Fixture com datasource mockado"""
        datasource = Mock()
        return datasource

    @pytest.fixture
    def controller(self, mock_datasource):
        """Fixture com controller"""
        return UrlController(mock_datasource)

    @pytest.fixture
    def valid_request_dto(self):
        """Fixture com UrlRequestDto válido"""
        return UrlRequestDto(
            file_name="test_video.mp4",
            action="upload"
        )

    def test_controller_init(self, mock_datasource):
        """Testa inicialização do controller"""
        controller = UrlController(mock_datasource)

        assert controller.datasource == mock_datasource

    def test_generate_presigned_url_success(self, controller, mock_datasource, valid_request_dto):
        """Testa geração de URL presigned com sucesso"""
        # Mock do gateway
        mock_url = Url(
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/presigned-url",
            fields={"expireIn": 900, "s3Key": "uploads/test_video.mp4"}
        )

        with patch.object(UrlGateway, 'generate_upload_presigned_url', return_value=mock_url):
            result = controller.generate_presigned_url(valid_request_dto)

        assert isinstance(result, dict)
        assert result['url'] == "https://s3.amazonaws.com/presigned-url"
        assert result['FileName'] == "test_video.mp4"
        assert result['action'] == "upload"
        assert result['method'] == "POST"
        assert result['expiresIn'] == 900
        assert result['s3Key'] == "uploads/test_video.mp4"

    def test_generate_presigned_url_with_different_actions(self, controller, mock_datasource):
        """Testa geração de URL com diferentes operações"""
        actions = ["upload", "download"]

        for action in actions:
            request_dto = UrlRequestDto(
                file_name="video.mp4",
                action=action
            )

            mock_url = Url(
                file_name="video.mp4",
                action=action,
                method="POST",
                url_endpoint="https://s3.amazonaws.com/url",
                fields={"expireIn": 900, "s3Key": "path/video.mp4"}
            )

            method_name = "generate_upload_presigned_url" if action == "upload" else "generate_download_presigned_url"
            with patch.object(UrlGateway, method_name, return_value=mock_url):
                result = controller.generate_presigned_url(request_dto)

            assert result['action'] == action

    def test_generate_presigned_url_with_different_methods(self, controller, mock_datasource):
        """Testa geração de URL com diferentes métodos HTTP"""
        methods = ["GET", "POST", "PUT", "DELETE"]

        for method in methods:
            request_dto = UrlRequestDto(
                file_name="video.mp4",
                action="upload"
            )

            mock_url = Url(
                file_name="video.mp4",
                action="upload",
                method=method,
                url_endpoint="https://s3.amazonaws.com/url",
                fields={"expireIn": 900, "s3Key": "path/video.mp4"}
            )

            with patch.object(UrlGateway, 'generate_upload_presigned_url', return_value=mock_url):
                result = controller.generate_presigned_url(request_dto)

            assert result['method'] == method

    def test_generate_presigned_url_preserves_filename(self, controller, mock_datasource):
        """Testa que o nome do arquivo é preservado"""
        request_dto = UrlRequestDto(
            file_name="my_special_video.mp4",
            action="upload")

        mock_url = Url(
            file_name="my_special_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/url",
            fields={"expireIn": 900, "s3Key": "uploads/my_special_video.mp4"}
        )

        with patch.object(UrlGateway, 'generate_upload_presigned_url', return_value=mock_url):
            result = controller.generate_presigned_url(request_dto)

        assert result['FileName'] == "my_special_video.mp4"

    def test_generate_presigned_url_with_complex_fields(self, controller, mock_datasource, valid_request_dto):
        """Testa geração de URL com fields complexos"""
        complex_fields = {
            "expireIn": 3600,
            "s3Key": "uploads/videos/2026/02/04/video.mp4"
        }

        mock_url = Url(
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/url",
            fields=complex_fields
        )

        with patch.object(UrlGateway, 'generate_upload_presigned_url', return_value=mock_url):
            result = controller.generate_presigned_url(valid_request_dto)

        assert result['expiresIn'] == 3600
        assert result['s3Key'] == "uploads/videos/2026/02/04/video.mp4"

    def test_controller_uses_gateway(self, controller, mock_datasource, valid_request_dto):
        """Testa que o controller usa o gateway corretamente"""
        mock_url = Url(
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/url",
            fields={"expireIn": 900, "s3Key": "uploads/test_video.mp4"}
        )

        with patch.object(UrlGateway, 'generate_upload_presigned_url', return_value=mock_url):
            controller.generate_presigned_url(valid_request_dto)


    def test_controller_uses_presenter(self, controller, mock_datasource, valid_request_dto):
        """Testa que o controller usa o presenter corretamente"""
        mock_url = Url(
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/url",
            fields={"expireIn": 900, "s3Key": "uploads/test_video.mp4"}
        )

        with patch.object(UrlGateway, 'generate_upload_presigned_url', return_value=mock_url):
            with patch.object(UrlPresenter, 'return_generate_presigned_url') as mock_presenter:
                mock_presenter.return_value = {
                    "url": "https://s3.amazonaws.com/url",
                    "FileName": "test_video.mp4",
                    "action": "upload",
                    "method": "POST",
                    "expiresIn": 900,
                    "s3Key": "uploads/test_video.mp4"
                }

                controller.generate_presigned_url(valid_request_dto)

                mock_presenter.assert_called_once_with(mock_url)
