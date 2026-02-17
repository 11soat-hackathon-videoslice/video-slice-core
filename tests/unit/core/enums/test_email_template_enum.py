"""Testes unitários para EmailTemplateEnum"""
import pytest
from core.enums.email_template_enum import EmailTemplateEnum


@pytest.mark.unit
class TestEmailTemplateEnum:
    """Testes para EmailTemplateEnum"""

    def test_enum_has_update_status_value(self):
        """Testa que enum possui valor PROCESSING"""
        assert hasattr(EmailTemplateEnum, 'PROCESSING')
        assert EmailTemplateEnum.PROCESSING is not None

    def test_enum_has_failed_value(self):
        """Testa que enum possui valor FAILED"""
        assert hasattr(EmailTemplateEnum, 'FAILED')
        assert EmailTemplateEnum.FAILED is not None

    def test_enum_has_finished_value(self):
        """Testa que enum possui valor FINISHED"""
        assert hasattr(EmailTemplateEnum, 'FINISHED')
        assert EmailTemplateEnum.FINISHED is not None

    def test_enum_values_are_different(self):
        """Testa que valores do enum são diferentes"""
        assert EmailTemplateEnum.PROCESSING != EmailTemplateEnum.FAILED
        assert EmailTemplateEnum.PROCESSING != EmailTemplateEnum.FINISHED
        assert EmailTemplateEnum.FAILED != EmailTemplateEnum.FINISHED

    def test_enum_name_property(self):
        """Testa propriedade name dos valores do enum"""
        assert EmailTemplateEnum.PROCESSING.name == 'PROCESSING'
        assert EmailTemplateEnum.FAILED.name == 'FAILED'
        assert EmailTemplateEnum.FINISHED.name == 'FINISHED'

    def test_enum_can_be_compared(self):
        """Testa que valores do enum podem ser comparados"""
        template1 = EmailTemplateEnum.PROCESSING
        template2 = EmailTemplateEnum.PROCESSING
        template3 = EmailTemplateEnum.FAILED
        assert template1 == template2
        assert template1 != template3

    def test_enum_can_be_used_in_list(self):
        """Testa que enum pode ser usado em lista"""
        templates = [EmailTemplateEnum.PROCESSING, EmailTemplateEnum.FAILED]
        assert EmailTemplateEnum.PROCESSING in templates
        assert EmailTemplateEnum.FINISHED not in templates

