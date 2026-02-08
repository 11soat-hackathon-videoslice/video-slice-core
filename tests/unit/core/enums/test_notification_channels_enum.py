"""Testes unitários para NotificationChannelsEnum"""
import pytest
from core.enums.notification_channels_enum import NotificationChannelsEnum


@pytest.mark.unit
class TestNotificationChannelsEnum:
    """Testes para NotificationChannelsEnum"""

    def test_enum_has_email_value(self):
        """Testa que enum possui valor EMAIL"""
        assert hasattr(NotificationChannelsEnum, 'EMAIL')
        assert NotificationChannelsEnum.EMAIL is not None

    def test_enum_has_web_value(self):
        """Testa que enum possui valor WEB"""
        assert hasattr(NotificationChannelsEnum, 'WEB')
        assert NotificationChannelsEnum.WEB is not None

    def test_enum_email_value_is_correct(self):
        """Testa que valor EMAIL está correto"""
        assert NotificationChannelsEnum.EMAIL.value == 'email'

    def test_enum_web_value_is_correct(self):
        """Testa que valor WEB está correto"""
        assert NotificationChannelsEnum.WEB.value == 'web'

    def test_enum_values_are_different(self):
        """Testa que valores do enum são diferentes"""
        assert NotificationChannelsEnum.EMAIL != NotificationChannelsEnum.WEB

    def test_enum_name_property(self):
        """Testa propriedade name dos valores do enum"""
        assert NotificationChannelsEnum.EMAIL.name == 'EMAIL'
        assert NotificationChannelsEnum.WEB.name == 'WEB'

    def test_enum_can_be_compared(self):
        """Testa que valores do enum podem ser comparados"""
        channel1 = NotificationChannelsEnum.EMAIL
        channel2 = NotificationChannelsEnum.EMAIL
        channel3 = NotificationChannelsEnum.WEB
        assert channel1 == channel2
        assert channel1 != channel3

    def test_enum_can_be_used_in_list(self):
        """Testa que enum pode ser usado em lista"""
        channels = [NotificationChannelsEnum.EMAIL]
        assert NotificationChannelsEnum.EMAIL in channels
        assert NotificationChannelsEnum.WEB not in channels

    def test_enum_can_be_used_in_dict_key(self):
        """Testa que enum pode ser usado como chave de dicionário"""
        config = {
            NotificationChannelsEnum.EMAIL: "email_config",
            NotificationChannelsEnum.WEB: "web_config"
        }
        assert config[NotificationChannelsEnum.EMAIL] == "email_config"
        assert config[NotificationChannelsEnum.WEB] == "web_config"

