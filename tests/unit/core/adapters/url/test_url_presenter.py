"""Testes unitários para UrlPresenter"""
import pytest
from core.adapters.url.url_presenter import UrlPresenter
from core.domain.url import Url
from core.dtos.url_dto import UrlResponseDto


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
            url_endpoint="https://s3.amazonaws.com/presigned-url"
        )

        result = presenter.return_generate_presigned_url(url)

        assert isinstance(result, UrlResponseDto)
        assert result.url_endpoint == "https://s3.amazonaws.com/presigned-url"
        assert result.file_name == "test_video.mp4"
        assert result.action == "upload"
        assert result.method == "POST"

    def test_return_generate_presigned_url_with_fields(self, presenter):
        """Testa retorno de URL com fields"""
        fields = {
            "key": "uploads/test_video.mp4",
            "bucket": "my-bucket"
        }

        url = Url(
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/presigned-url",
            fields=fields
        )

        result = presenter.return_generate_presigned_url(url)

        assert result.fields == fields

    def test_return_generate_presigned_url_without_fields(self, presenter):
        """Testa retorno de URL sem fields"""
        url = Url(
            file_name="video.mp4",
            action="download",
            method="GET",
            url_endpoint="https://s3.amazonaws.com/url"
        )

        result = presenter.return_generate_presigned_url(url)

        assert result.fields is None

    def test_return_generate_presigned_url_preserves_all_data(self, presenter):
        """Testa que todos os dados são preservados"""
        fields = {
            "key": "uploads/video.mp4",
            "bucket": "vdsc-prd-s3-bucket",
            "acl": "private"
        }

        url = Url(
            file_name="important_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.us-east-1.amazonaws.com/presigned-url",
            fields=fields
        )

        result = presenter.return_generate_presigned_url(url)

        assert result.url_endpoint == url.url_endpoint
        assert result.file_name == url.file_name
        assert result.action == url.action
        assert result.method == url.method
        assert result.fields == url.fields

    def test_return_generate_presigned_url_with_different_operations(self, presenter):
        """Testa retorno com diferentes operações"""
        operations = ["upload", "download", "delete"]

        for operation in operations:
            url = Url(
                file_name="video.mp4",
                action=operation,
                method="POST",
                url_endpoint="https://s3.amazonaws.com/url"
            )

            result = presenter.return_generate_presigned_url(url)

            assert result.action == operation

    def test_return_generate_presigned_url_with_different_methods(self, presenter):
        """Testa retorno com diferentes métodos HTTP"""
        methods = ["GET", "POST", "PUT", "DELETE"]

        for method in methods:
            url = Url(
                file_name="video.mp4",
                action="upload",
                method=method,
                url_endpoint="https://s3.amazonaws.com/url"
            )

            result = presenter.return_generate_presigned_url(url)

            assert result.method == method

    def test_return_generate_presigned_url_with_complex_fields(self, presenter):
        """Testa retorno com fields complexos"""
        complex_fields = {
            "key": "uploads/videos/2026/02/04/video.mp4",
            "bucket": "vdsc-prd-s3-bucket",
            "acl": "private",
            "content-type": "video/mp4",
            "expires": "3600",
            "x-amz-meta-custom": "value"
        }

        url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/url",
            fields=complex_fields
        )

        result = presenter.return_generate_presigned_url(url)

        assert result.fields == complex_fields

    def test_return_generate_presigned_url_with_empty_url_endpoint(self, presenter):
        """Testa retorno com URL endpoint vazio"""
        url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST",
            url_endpoint=""
        )

        result = presenter.return_generate_presigned_url(url)

        assert result.url_endpoint == ""

    def test_return_generate_presigned_url_returns_new_instance(self, presenter):
        """Testa que retorna nova instância de UrlResponseDto"""
        url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/url"
        )

        result1 = presenter.return_generate_presigned_url(url)
        result2 = presenter.return_generate_presigned_url(url)

        # Verifica que são instâncias diferentes
        assert result1 is not result2
        # Mas com os mesmos dados
        assert result1.to_dict() == result2.to_dict()

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
                url_endpoint="https://s3.amazonaws.com/url"
            )

            result = presenter.return_generate_presigned_url(url)

            assert result.file_name == file_name
