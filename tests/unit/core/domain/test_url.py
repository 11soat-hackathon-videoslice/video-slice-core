"""Testes unitários para a classe Url do domínio"""
import pytest
from core.domain.url import Url
from core.dtos.url_dto import UrlRequestDto, UrlResponseDto


@pytest.mark.unit
class TestUrl:
    """Testes para a classe Url do domínio"""

    def test_create_url_with_required_fields(self):
        """Testa criação de Url apenas com campos obrigatórios"""
        url = Url(
            file_name="test_video.mp4",
            action="upload",
            method="POST"
        )

        assert url.file_name == "test_video.mp4"
        assert url.action == "upload"
        assert url.url_endpoint is None
        assert url.fields is None

    def test_create_url_with_all_fields(self):
        """Testa criação de Url com todos os campos"""
        fields = {"key": "uploads/test_video.mp4", "bucket": "my-bucket"}
        url = Url(
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/presigned-url",
            fields=fields
        )

        assert url.file_name == "test_video.mp4"
        assert url.action == "upload"
        assert url.url_endpoint == "https://s3.amazonaws.com/presigned-url"
        assert url.fields == fields

    def test_create_url_with_empty_strings(self):
        """Testa criação de Url com strings vazias"""
        url = Url(
            file_name="",
            action="",
            method=""
        )

        assert url.file_name == ""
        assert url.action == ""

    def test_url_endpoint_optional(self):
        """Testa que url_endpoint é opcional"""
        url = Url(
            file_name="video.mp4",
            action="download",
            method="GET"
        )

        assert url.url_endpoint is None

    def test_fields_optional(self):
        """Testa que fields é opcional"""
        url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST"
        )

        assert url.fields is None


@pytest.mark.unit
class TestUrlFromRequest:
    """Testes para o método from_request"""

    def test_from_request_creates_url(self):
        """Testa criação de Url a partir de UrlRequestDto"""
        request_dto = UrlRequestDto(
            file_name="test_video.mp4",
            action="upload"
        )

        url = Url.from_request(request_dto)

        assert url.file_name == "test_video.mp4"
        assert url.action == "upload"
        assert url.url_endpoint is None
        assert url.fields is None

    def test_from_request_with_different_operations(self):
        """Testa from_request com diferentes operações"""
        operations = ["upload", "download", "delete"]

        for operation in operations:
            request_dto = UrlRequestDto(
                file_name="video.mp4",
                action=operation
            )
            url = Url.from_request(request_dto)
            assert url.action == operation



@pytest.mark.unit
class TestUrlFromResponse:
    """Testes para o método from_response"""

    def test_from_response_creates_url(self):
        """Testa criação de Url a partir de UrlResponseDto"""
        response_dto = UrlResponseDto(
            url_endpoint="https://s3.amazonaws.com/presigned-url",
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            fields={"key": "uploads/test_video.mp4"}
        )

        url = Url.from_response(response_dto)

        assert url.url_endpoint == "https://s3.amazonaws.com/presigned-url"
        assert url.file_name == "test_video.mp4"
        assert url.action == "upload"
        assert url.method == "POST"
        assert url.fields == {"key": "uploads/test_video.mp4"}

    def test_from_response_without_fields(self):
        """Testa from_response sem fields"""
        response_dto = UrlResponseDto(
            url_endpoint="https://s3.amazonaws.com/presigned-url",
            file_name="test_video.mp4",
            action="download",
            method="GET"
        )

        url = Url.from_response(response_dto)

        assert url.url_endpoint == "https://s3.amazonaws.com/presigned-url"
        assert url.fields is None

    def test_from_response_preserves_all_data(self):
        """Testa que from_response preserva todos os dados"""
        fields = {
            "key": "uploads/video.mp4",
            "bucket": "my-bucket",
            "acl": "private"
        }
        response_dto = UrlResponseDto(
            url_endpoint="https://example.com/url",
            file_name="video.mp4",
            action="upload",
            method="POST",
            fields=fields
        )

        url = Url.from_response(response_dto)

        assert url.url_endpoint == response_dto.url_endpoint
        assert url.file_name == response_dto.file_name
        assert url.action == response_dto.action
        assert url.method == response_dto.method
        assert url.fields == fields


@pytest.mark.unit
class TestUrlToDict:
    """Testes para o mét0d0 to_dict"""

    def test_to_dict_with_all_fields(self):
        """Testa conversão para dicionário com todos os campos"""
        fields = {"key": "uploads/video.mp4"}
        url = Url(
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/presigned-url",
            fields=fields
        )

        result = url.to_dict()

        assert result == {
            "url_endpoint": "https://s3.amazonaws.com/presigned-url",
            "file_name": "test_video.mp4",
            "action": "upload",
            "method": "POST",
            "fields": fields
        }

    def test_to_dict_with_none_values(self):
        """Testa conversão para dicionário com valores None"""
        url = Url(
            file_name="video.mp4",
            action="download",
            method="GET"
        )

        result = url.to_dict()

        assert result["url_endpoint"] is None
        assert result["fields"] is None
        assert result["file_name"] == "video.mp4"

    def test_to_dict_preserves_empty_strings(self):
        """Testa que to_dict preserva strings vazias"""
        url = Url(
            file_name="",
            action="",
            method=""
        )

        result = url.to_dict()

        assert result["file_name"] == ""
        assert result["action"] == ""
        assert result["method"] == ""


@pytest.mark.unit
class TestUrlFromDict:
    """Testes para o método from_dict"""

    def test_from_dict_with_all_fields(self):
        """Testa criação de Url a partir de dicionário completo"""
        data = {
            "url_endpoint": "https://s3.amazonaws.com/presigned-url",
            "file_name": "test_video.mp4",
            "action": "upload",
            "method": "POST",
            "fields": {"key": "uploads/video.mp4"}
        }

        url = Url.from_dict(data)

        assert url.url_endpoint == "https://s3.amazonaws.com/presigned-url"
        assert url.file_name == "test_video.mp4"
        assert url.action == "upload"
        assert url.fields == {"key": "uploads/video.mp4"}

    def test_from_dict_with_required_fields_only(self):
        """Testa from_dict apenas com campos obrigatórios"""
        data = {
            "file_name": "video.mp4",
            "action": "download",
            "method": "GET"
        }

        url = Url.from_dict(data)

        assert url.file_name == "video.mp4"
        assert url.action == "download"
        assert url.url_endpoint is None
        assert url.fields is None

    def test_from_dict_with_missing_optional_fields(self):
        """Testa from_dict com campos opcionais ausentes"""
        data = {
            "file_name": "video.mp4",
            "action": "upload",
            "method": "POST"
        }

        url = Url.from_dict(data)

        assert url.url_endpoint is None
        assert url.fields is None

    def test_from_dict_roundtrip(self):
        """Testa que from_dict e to_dict são reversíveis"""
        original_data = {
            "url_endpoint": "https://example.com/url",
            "file_name": "video.mp4",
            "action": "upload",
            "method": "POST",
            "fields": {"key": "value"}
        }

        url = Url.from_dict(original_data)
        result_data = url.to_dict()

        assert result_data == original_data


@pytest.mark.unit
class TestUrlUpdatePresignedData:
    """Testes para o método update_presigned_data"""

    def test_update_presigned_data_with_url_only(self):
        """Testa atualização apenas da URL"""
        url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST"
        )

        url.update_presigned_data("https://s3.amazonaws.com/new-url")

        assert url.url_endpoint == "https://s3.amazonaws.com/new-url"
        assert url.fields is None

    def test_update_presigned_data_with_url_and_fields(self):
        """Testa atualização da URL com fields"""
        url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST"
        )

        new_fields = {"key": "uploads/video.mp4", "bucket": "my-bucket"}
        url.update_presigned_data("https://s3.amazonaws.com/new-url", new_fields)

        assert url.url_endpoint == "https://s3.amazonaws.com/new-url"
        assert url.fields == new_fields

    def test_update_presigned_data_replaces_existing_url(self):
        """Testa que update_presigned_data substitui URL existente"""
        url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://old-url.com"
        )

        url.update_presigned_data("https://new-url.com")

        assert url.url_endpoint == "https://new-url.com"

    def test_update_presigned_data_replaces_existing_fields(self):
        """Testa que update_presigned_data substitui fields existentes"""
        url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST",
            fields={"old_key": "old_value"}
        )

        new_fields = {"new_key": "new_value"}
        url.update_presigned_data("https://url.com", new_fields)

        assert url.fields == new_fields

    def test_update_presigned_data_preserves_other_attributes(self):
        """Testa que update_presigned_data preserva outros atributos"""
        url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST"
        )

        url.update_presigned_data("https://new-url.com", {"key": "value"})

        assert url.file_name == "video.mp4"
        assert url.action == "upload"

    def test_update_presigned_data_with_empty_url(self):
        """Testa atualização com URL vazia"""
        url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST"
        )

        url.update_presigned_data("")

        assert url.url_endpoint == ""

    def test_update_presigned_data_multiple_times(self):
        """Testa múltiplas atualizações consecutivas"""
        url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST"
        )

        url.update_presigned_data("https://url1.com", {"key1": "value1"})
        assert url.url_endpoint == "https://url1.com"
        assert url.fields == {"key1": "value1"}

        url.update_presigned_data("https://url2.com", {"key2": "value2"})
        assert url.url_endpoint == "https://url2.com"
        assert url.fields == {"key2": "value2"}


@pytest.mark.unit
class TestUrlIntegration:
    """Testes de integração para a classe Url"""

    def test_full_workflow_from_request_to_response(self):
        """Testa workflow completo de request para response"""
        # Cria request
        request_dto = UrlRequestDto(
            file_name="video.mp4",
            action="upload"
        )

        # Cria Url a partir do request
        url = Url.from_request(request_dto)

        # Atualiza com dados presigned
        url.update_presigned_data(
            "https://s3.amazonaws.com/presigned-url",
            {"key": "uploads/video.mp4"}
        )

        # Converte para dict
        url_dict = url.to_dict()

        # Verifica resultado final
        assert url_dict["file_name"] == "video.mp4"
        assert url_dict["action"] == "upload"
        assert url_dict["url_endpoint"] == "https://s3.amazonaws.com/presigned-url"
        assert url_dict["fields"] == {"key": "uploads/video.mp4"}

    def test_roundtrip_request_to_dict_to_url(self):
        """Testa conversão completa: request -> url -> dict -> url"""
        # Request inicial
        request_dto = UrlRequestDto(
            file_name="test.mp4",
            action="download"
        )

        # Primeira conversão
        url1 = Url.from_request(request_dto)
        url1.update_presigned_data("https://example.com/url")

        # Converte para dict
        url_dict = url1.to_dict()

        # Cria nova instância a partir do dict
        url2 = Url.from_dict(url_dict)

        # Verifica que são equivalentes
        assert url2.file_name == url1.file_name
        assert url2.action == url1.action
        assert url2.method == url1.method
        assert url2.url_endpoint == url1.url_endpoint
        assert url2.fields == url1.fields

    def test_url_with_complex_fields(self):
        """Testa Url com fields complexos"""
        complex_fields = {
            "key": "uploads/videos/2026/02/04/video.mp4",
            "bucket": "vdsc-prd-s3-bucket",
            "acl": "private",
            "content-type": "video/mp4",
            "expires": "3600"
        }

        url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.us-east-1.amazonaws.com/presigned-url",
            fields=complex_fields
        )

        # Verifica que fields complexos são preservados
        assert url.fields == complex_fields

        # Verifica preservação em conversões
        url_dict = url.to_dict()
        url_restored = Url.from_dict(url_dict)
        assert url_restored.fields == complex_fields

    def test_url_equality_through_dict(self):
        """Testa que duas URLs com mesmos dados são equivalentes via dict"""
        url1 = Url(
            file_name="video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://example.com",
            fields={"key": "value"}
        )

        url2 = Url.from_dict(url1.to_dict())

        assert url1.to_dict() == url2.to_dict()

    def test_url_with_different_file_types(self):
        """Testa Url com diferentes tipos de arquivo"""
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
                method="POST"
            )
            assert url.file_name == file_name

    def test_url_independence(self):
        """Testa que múltiplas instâncias de Url são independentes"""
        url1 = Url(
            file_name="video1.mp4",
            action="upload",
            method="POST"
        )
        url2 = Url(
            file_name="video2.mp4",
            action="download",
            method="GET"
        )

        url1.update_presigned_data("https://url1.com", {"key1": "value1"})
        url2.update_presigned_data("https://url2.com", {"key2": "value2"})

        # Verifica que as instâncias não interferem entre si
        assert url1.url_endpoint == "https://url1.com"
        assert url1.fields == {"key1": "value1"}
        assert url2.url_endpoint == "https://url2.com"
        assert url2.fields == {"key2": "value2"}
