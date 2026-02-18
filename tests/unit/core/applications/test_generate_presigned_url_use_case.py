"""Testes unitários para GeneratePresignedURLUseCase"""
import pytest
from unittest.mock import Mock, patch
from core.applications.generate_pressigned_url_use_case import GeneratePresignedURLUseCase
from core.domain.url import Url
from core.dtos.url_dto import UrlRequestDto
from core.exceptions.vdsc_exceptions import VdscException
from core.enums.vdsc_status_enum import VdscStatusEnum


@pytest.mark.unit
class TestGeneratePresignedURLUseCase:
    """Testes para a classe GeneratePresignedURLUseCase"""

    @pytest.fixture
    def mock_gateway(self):
        """Fixture com gateway mockado"""
        gateway = Mock()
        gateway.generate_presigned_url = Mock()
        return gateway

    @pytest.fixture
    def use_case(self, mock_gateway):
        """Fixture com use case"""
        return GeneratePresignedURLUseCase(mock_gateway)

    @pytest.fixture
    def valid_request_dto(self):
        """Fixture com UrlRequestDto válido"""
        return UrlRequestDto(
            file_name="test_video.mp4",
            action="upload"
        )

    def test_use_case_init(self, mock_gateway):
        """Testa inicialização do use case"""
        use_case = GeneratePresignedURLUseCase(mock_gateway)

        assert use_case.gateway == mock_gateway

    def test_execute_success(self, use_case, mock_gateway, valid_request_dto):
        """Testa execução bem-sucedida do use case"""
        expected_url = Url(
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/presigned-url",
            fields={"key": "uploads/test_video.mp4"}
        )
        mock_gateway.generate_upload_presigned_url.return_value = expected_url

        result = use_case.execute(valid_request_dto)

        assert isinstance(result, Url)
        assert result.file_name == "test_video.mp4"
        assert result.action == "upload"
        assert result.method == "POST"
        assert result.url_endpoint == "https://s3.amazonaws.com/presigned-url"
        mock_gateway.generate_upload_presigned_url.assert_called_once()

    def test_execute_calls_gateway_with_url_object(self, use_case, mock_gateway, valid_request_dto):
        """Testa que execute chama o gateway com objeto Url"""
        expected_url = Url(
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/url"
        )
        mock_gateway.generate_upload_presigned_url.return_value = expected_url

        use_case.execute(valid_request_dto)

        call_args = mock_gateway.generate_upload_presigned_url.call_args
        assert call_args is not None
        assert len(call_args.args) > 0
        assert isinstance(call_args.args[0], Url)

    def test_execute_with_upload_operation(self, use_case, mock_gateway):
        """Testa execução com operação de upload"""
        request_dto = UrlRequestDto(
            file_name="video.mp4",
            action="upload"
        )

        expected_url = Url(
            file_name="video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/upload-url"
        )
        mock_gateway.generate_upload_presigned_url.return_value = expected_url

        result = use_case.execute(request_dto)

        assert result.action == "upload"
        assert result.url_endpoint == "https://s3.amazonaws.com/upload-url"
        mock_gateway.generate_upload_presigned_url.assert_called_once()

    def test_execute_with_download_operation(self, use_case, mock_gateway):
        """Testa execução com operação de download"""
        request_dto = UrlRequestDto(
            file_name="video.mp4",
            action="download"
        )

        expected_url = Url(
            file_name="video.mp4",
            action="download",
            method="GET",
            url_endpoint="https://s3.amazonaws.com/download-url"
        )
        mock_gateway.generate_download_presigned_url.return_value = expected_url

        result = use_case.execute(request_dto)

        assert result.action == "download"
        assert result.method == "GET"
        mock_gateway.generate_download_presigned_url.assert_called_once()

    def test_execute_preserves_filename(self, use_case, mock_gateway):
        """Testa que o nome do arquivo é preservado"""
        request_dto = UrlRequestDto(
            file_name="important_video_2026.mp4",
            action="upload"
        )

        expected_url = Url(
            file_name="important_video_2026.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/url"
        )
        mock_gateway.generate_upload_presigned_url.return_value = expected_url

        result = use_case.execute(request_dto)

        assert result.file_name == "important_video_2026.mp4"

    def test_execute_with_fields(self, use_case, mock_gateway, valid_request_dto):
        """Testa execução com fields adicionais"""
        fields = {
            "key": "uploads/videos/2026-02-04T00:00:00Z/video.mp4",
            "bucket": "vdsc-prd-s3-bucket",
            "acl": "private",
            "content-type": "video/mp4"
        }

        expected_url = Url(
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/url",
            fields=fields
        )
        mock_gateway.generate_upload_presigned_url.return_value = expected_url

        result = use_case.execute(valid_request_dto)

        assert result.fields == fields

    def test_execute_raises_vdsc_exception_on_gateway_error(self, use_case, mock_gateway, valid_request_dto):
        """Testa que VdscException é lançada quando o gateway falha"""
        mock_gateway.generate_upload_presigned_url.side_effect = Exception("Gateway error")

        with pytest.raises(VdscException) as exc_info:
            use_case.execute(valid_request_dto)

        assert "Falha ao gerar URL presigned" in str(exc_info.value)
        assert exc_info.value.info == VdscStatusEnum.ERROR

    def test_execute_logs_error_on_exception(self, use_case, mock_gateway, valid_request_dto):
        """Testa que erros são logados quando ocorre exceção"""
        mock_gateway.generate_upload_presigned_url.side_effect = Exception("Test error")

        with patch('core.applications.generate_pressigned_url_use_case.logger') as mock_logger:
            with pytest.raises(VdscException):
                use_case.execute(valid_request_dto)

            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args[0][0]
            assert "Erro ao gerar URL presigned" in call_args

    def test_execute_includes_metadata_in_exception(self, use_case, mock_gateway, valid_request_dto):
        """Testa que metadados são incluídos na exceção"""
        mock_gateway.generate_upload_presigned_url.side_effect = Exception("Test error")

        with pytest.raises(VdscException) as exc_info:
            use_case.execute(valid_request_dto)

        assert exc_info.value.metadata == valid_request_dto.to_dict()
        assert exc_info.value.metadata["file_name"] == "test_video.mp4"
        assert exc_info.value.metadata["action"] == "upload"

    def test_execute_with_different_methods(self, use_case, mock_gateway):
        """Testa execução com diferentes métodos HTTP"""
        methods = ["GET", "POST", "PUT", "DELETE"]

        for method in methods:
            request_dto = UrlRequestDto(
                file_name="video.mp4",
                action="upload"
            )

            expected_url = Url(
                file_name="video.mp4",
                action="upload",
                method=method,
                url_endpoint="https://s3.amazonaws.com/url"
            )
            mock_gateway.generate_upload_presigned_url.return_value = expected_url

            result = use_case.execute(request_dto)

            assert result.method == method

    def test_execute_with_different_file_types(self, use_case, mock_gateway):
        """Testa execução com diferentes tipos de arquivo"""
        file_names = [
            "video.mp4",
            "movie.avi",
            "clip.mov",
            "presentation.mkv"
        ]

        for file_name in file_names:
            request_dto = UrlRequestDto(
                file_name=file_name,
                action="upload"
            )

            expected_url = Url(
                file_name=file_name,
                action="upload",
                method="POST",
                url_endpoint="https://s3.amazonaws.com/url"
            )
            mock_gateway.generate_upload_presigned_url.return_value = expected_url

            result = use_case.execute(request_dto)

            assert result.file_name == file_name

    def test_execute_returns_gateway_result(self, use_case, mock_gateway, valid_request_dto):
        """Testa que execute retorna o resultado do gateway"""
        expected_url = Url(
            file_name="test_video.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.us-east-1.amazonaws.com/presigned-url",
            fields={"key": "uploads/test_video.mp4", "bucket": "vdsc-prd-s3-bucket"}
        )
        mock_gateway.generate_upload_presigned_url.return_value = expected_url

        result = use_case.execute(valid_request_dto)

        assert result == expected_url
        assert result.url_endpoint == expected_url.url_endpoint
        assert result.fields == expected_url.fields

    def test_execute_handles_empty_fields(self, use_case, mock_gateway):
        """Testa execução quando fields é None"""
        request_dto = UrlRequestDto(
            file_name="test_video.mp4",
            action="download"
        )

        expected_url = Url(
            file_name="test_video.mp4",
            action="download",
            method="GET",
            url_endpoint="https://s3.amazonaws.com/url",
            fields=None
        )
        mock_gateway.generate_download_presigned_url.return_value = expected_url

        result = use_case.execute(request_dto)

        assert result.fields is None

    def test_execute_with_special_characters_in_filename(self, use_case, mock_gateway):
        """Testa execução com caracteres especiais no nome do arquivo"""
        request_dto = UrlRequestDto(
            file_name="vídeo-teste_2026-02-04.mp4",
            action="upload"
        )

        expected_url = Url(
            file_name="vídeo-teste_2026-02-04.mp4",
            action="upload",
            method="POST",
            url_endpoint="https://s3.amazonaws.com/url"
        )
        mock_gateway.generate_upload_presigned_url.return_value = expected_url

        result = use_case.execute(request_dto)

        assert result.file_name == "vídeo-teste_2026-02-04.mp4"

    def test_execute_raises_value_error_for_unsupported_operation(self, use_case, mock_gateway):
        """Testa que ValueError é lançada para operação não suportada"""
        request_dto = UrlRequestDto(
            file_name="test_video.mp4",
            action="delete"
        )

        with pytest.raises(VdscException) as exc_info:
            use_case.execute(request_dto)

        assert "Operação não suportada" in str(exc_info.value)

