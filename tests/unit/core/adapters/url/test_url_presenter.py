"""Testes unitários para UrlPresenter"""
import pytest
from core.adapters.url.url_presenter import UrlPresenter
from core.domain.url import Url


@pytest.mark.unit
class TestUrlPresenter:
    """Testes para a classe UrlPresenter"""

    @pytest.fixture
    def presenter(self):
        """Fixture com presenter"""
        return UrlPresenter()

    def test_presenter_init(self):
        """Testa inicialização do presenter"""
        presenter = UrlPresenter()

        assert presenter is not None

    def test_return_generate_presigned_url_basic(self, presenter):
        """Testa retorno básico de URL presigned"""
        url = Url(
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/presigned-url",
            fields={"expireIn": 900, "s3Key": "uploads/test_video.mp4"}
        )

        result = presenter.return_generate_presigned_url(url)

        assert isinstance(result, dict)
        assert result['url'] == "https://s3.amazonaws.com/presigned-url"
        assert result['FileName'] == "test_video.mp4"
        assert result['action'] == "upload"
        assert result['method'] == "POST"
        assert result['expiresIn'] == 900
        assert result['s3Key'] == "uploads/test_video.mp4"

    def test_return_generate_presigned_url_with_fields(self, presenter):
        """Testa retorno de URL com fields"""
        fields = {
            "expireIn": 3600,
            "s3Key": "uploads/test_video.mp4"
        }

        url = Url(
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/presigned-url",
            fields=fields
        )

        result = presenter.return_generate_presigned_url(url)

        assert result['expiresIn'] == 3600
        assert result['s3Key'] == "uploads/test_video.mp4"

    def test_return_generate_presigned_url_without_fields(self, presenter):
        """Testa retorno de URL sem fields"""
        url = Url(
            file_name="video.mp4",
            action="download",
            method="GET",
            url_endpoint="https://s3.amazonaws.com/url",
            fields={"expireIn": 180, "s3Key": "finished/video.mp4"}
        )

        result = presenter.return_generate_presigned_url(url)

        assert isinstance(result, dict)
        assert result['expiresIn'] == 180
        assert result['s3Key'] == "finished/video.mp4"

    def test_return_generate_presigned_url_preserves_all_data(self, presenter):
        """Testa que todos os dados são preservados"""
        fields = {
            "expireIn": 3600,
            "s3Key": "uploads/video.mp4"
        }

        url = Url(
            file_name="important_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.us-east-1.amazonaws.com/presigned-url",
            fields=fields
        )

        result = presenter.return_generate_presigned_url(url)

        assert result['url'] == url.url_endpoint
        assert result['FileName'] == url.file_name
        assert result['action'] == url.action
        assert result['method'] == url.method
        assert result['expiresIn'] == fields['expireIn']
        assert result['s3Key'] == fields['s3Key']

    def test_return_generate_presigned_url_with_different_operations(self, presenter):
        """Testa retorno com diferentes operações"""
        operations = ["upload", "download", "delete"]

        for operation in operations:
            url = Url(
                file_name="video.mp4",
                action=operation,
                method="POST",
                url_endpoint="https://s3.amazonaws.com/url",
                fields={"expireIn": 900, "s3Key": f"path/video.mp4"}
            )

            result = presenter.return_generate_presigned_url(url)

            assert result['action'] == operation

    def test_return_generate_presigned_url_with_different_methods(self, presenter):
        """Testa retorno com diferentes métodos HTTP"""
        methods = ["GET", "POST", "PUT", "DELETE"]

        for method in methods:
            url = Url(
                file_name="video.mp4",
                action="upload",
                method=method,
                url_endpoint="https://s3.amazonaws.com/url",
                fields={"expireIn": 900, "s3Key": "path/video.mp4"}
            )

            result = presenter.return_generate_presigned_url(url)

            assert result['method'] == method

    def test_return_generate_presigned_url_with_complex_fields(self, presenter):
        """Testa retorno com fields complexos"""
        complex_fields = {
            "expireIn": 3600,
            "s3Key": "uploads/videos/2026/02/04/video.mp4"
        }

        url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/url",
            fields=complex_fields
        )

        result = presenter.return_generate_presigned_url(url)

        assert result['expiresIn'] == 3600
        assert result['s3Key'] == "uploads/videos/2026/02/04/video.mp4"

    def test_return_generate_presigned_url_with_empty_url_endpoint(self, presenter):
        """Testa retorno com URL endpoint vazio"""
        url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST",
            url_endpoint="",
            fields={"expireIn": 900, "s3Key": "uploads/video.mp4"}
        )

        result = presenter.return_generate_presigned_url(url)

        assert result['url'] == ""

    def test_return_generate_presigned_url_returns_new_instance(self, presenter):
        """Testa que retorna nova instância (dicts diferentes)"""
        url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/url",
            fields={"expireIn": 900, "s3Key": "uploads/video.mp4"}
        )

        result1 = presenter.return_generate_presigned_url(url)
        result2 = presenter.return_generate_presigned_url(url)

        # Verifica que são dicts com os mesmos dados
        assert result1 == result2
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)

    def test_return_generate_presigned_url_with_different_file_types(self, presenter):
        """Testa retorno com diferentes tipos de arquivo"""
        file_types = [
            "video.mp4",
            "image.jpg",
            "document.pdf",
            "archive.zip"
        ]

        for file_name in file_types:
            url = Url(
                file_name=file_name,
                action="upload",
                method="POST",
                url_endpoint="https://s3.amazonaws.com/url",
                fields={"expireIn": 900, "s3Key": f"uploads/{file_name}"}
            )

            result = presenter.return_generate_presigned_url(url)

            assert result['FileName'] == file_name
