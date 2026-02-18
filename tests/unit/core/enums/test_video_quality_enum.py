"""Testes unitários para VideoResize enum"""
import pytest
from core.enums.video_resize_enum import VideoResize


@pytest.mark.unit
class TestVideoQuality:
    """Testes para a enumeração de qualidade de vídeo"""

    def test_enum_values(self):
        """Testa se todos os valores do enum estão definidos corretamente"""
        assert VideoResize.ULTRA.value == "ultra"
        assert VideoResize.HIGH.value == "high"
        assert VideoResize.MEDIUM.value == "medium"
        assert VideoResize.LOW.value == "low"

    def test_is_valid_with_valid_quality(self):
        """Testa validação com qualidade válida"""
        assert VideoResize.is_valid("ultra") is True
        assert VideoResize.is_valid("high") is True
        assert VideoResize.is_valid("medium") is True
        assert VideoResize.is_valid("low") is True

    def test_is_valid_with_invalid_quality(self):
        """Testa validação com qualidade inválida"""
        assert VideoResize.is_valid("invalid") is False
        assert VideoResize.is_valid("") is False
        assert VideoResize.is_valid("HIGH") is False

    def test_get_all_values(self):
        """Testa obtenção de todos os valores"""
        all_values = VideoResize.get_all_values()
        assert len(all_values) == 4
        assert "ultra" in all_values
        assert "high" in all_values
        assert "medium" in all_values
        assert "low" in all_values

    def test_str_method(self):
        """Testa método __str__ do enum"""
        assert str(VideoResize.ULTRA) == "ultra"
        assert str(VideoResize.HIGH) == "high"

    def test_get_scale_factor(self):
        """Testa obtenção de fator de escala"""
        assert VideoResize.ULTRA.get_scale_factor() == "ultra"
        assert VideoResize.HIGH.get_scale_factor() == "high"
        assert VideoResize.MEDIUM.get_scale_factor() == "medium"
        assert VideoResize.LOW.get_scale_factor() == "low"

    def test_from_scale_valid(self):
        """Testa criação a partir de escala válida"""
        assert VideoResize.from_scale("ultra") == VideoResize.ULTRA
        assert VideoResize.from_scale("high") == VideoResize.HIGH
        assert VideoResize.from_scale("medium") == VideoResize.MEDIUM
        assert VideoResize.from_scale("low") == VideoResize.LOW

    def test_from_scale_invalid(self):
        """Testa criação a partir de escala inválida"""
        with pytest.raises(ValueError):
            VideoResize.from_scale("invalid")
