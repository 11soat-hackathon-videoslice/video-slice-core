"""Testes unitários para SendNotificationUseCaseFactory"""
import pytest
from unittest.mock import Mock
from core.applications.notification.send_notification_use_case_factory import SendNotificationUseCaseFactory
from core.applications.notification.send_notification_email_use_case import SendNotificationEmailUseCase
from core.applications.notification.send_notification_web_use_case import SendNotificationWebUseCase
from core.enums.notification_channels_enum import NotificationChannelsEnum


@pytest.mark.unit
class TestSendNotificationUseCaseFactory:
    """Testes para SendNotificationUseCaseFactory"""

    @pytest.fixture
    def mock_email_use_case(self):
        """Fixture com email use case mockado"""
        return Mock(spec=SendNotificationEmailUseCase)

    @pytest.fixture
    def mock_web_use_case(self):
        """Fixture com web use case mockado"""
        return Mock(spec=SendNotificationWebUseCase)

    def test_factory_created_with_use_cases_successfully(self, mock_email_use_case, mock_web_use_case):
        factory = SendNotificationUseCaseFactory(mock_email_use_case, mock_web_use_case)
        assert factory._use_cases is not None
        assert len(factory._use_cases) == 2

    def test_get_use_case_returns_email_use_case_for_email_channel(self, mock_email_use_case, mock_web_use_case):
        factory = SendNotificationUseCaseFactory(mock_email_use_case, mock_web_use_case)
        use_case = factory.get_use_case(NotificationChannelsEnum.EMAIL)
        assert use_case == mock_email_use_case

    def test_get_use_case_returns_web_use_case_for_web_channel(self, mock_email_use_case, mock_web_use_case):
        factory = SendNotificationUseCaseFactory(mock_email_use_case, mock_web_use_case)
        use_case = factory.get_use_case(NotificationChannelsEnum.WEB)
        assert use_case == mock_web_use_case

    def test_get_use_case_raises_error_for_unknown_channel(self, mock_email_use_case, mock_web_use_case):
        factory = SendNotificationUseCaseFactory(mock_email_use_case, mock_web_use_case)
        with pytest.raises(ValueError, match="Não encontrado caso de uso para o canal"):
            factory.get_use_case("UNKNOWN_CHANNEL")

    def test_get_use_case_raises_error_for_none_channel(self, mock_email_use_case, mock_web_use_case):
        factory = SendNotificationUseCaseFactory(mock_email_use_case, mock_web_use_case)
        with pytest.raises(ValueError, match="Não encontrado caso de uso para o canal"):
            factory.get_use_case(None)

    def test_factory_use_cases_dictionary_contains_email_key(self, mock_email_use_case, mock_web_use_case):
        factory = SendNotificationUseCaseFactory(mock_email_use_case, mock_web_use_case)
        assert NotificationChannelsEnum.EMAIL in factory._use_cases

    def test_factory_use_cases_dictionary_contains_web_key(self, mock_email_use_case, mock_web_use_case):
        factory = SendNotificationUseCaseFactory(mock_email_use_case, mock_web_use_case)
        assert NotificationChannelsEnum.WEB in factory._use_cases

    def test_get_use_case_for_email_returns_same_instance_multiple_times(self, mock_email_use_case, mock_web_use_case):
        factory = SendNotificationUseCaseFactory(mock_email_use_case, mock_web_use_case)
        use_case1 = factory.get_use_case(NotificationChannelsEnum.EMAIL)
        use_case2 = factory.get_use_case(NotificationChannelsEnum.EMAIL)
        assert use_case1 is use_case2

    def test_get_use_case_for_web_returns_same_instance_multiple_times(self, mock_email_use_case, mock_web_use_case):
        factory = SendNotificationUseCaseFactory(mock_email_use_case, mock_web_use_case)
        use_case1 = factory.get_use_case(NotificationChannelsEnum.WEB)
        use_case2 = factory.get_use_case(NotificationChannelsEnum.WEB)
        assert use_case1 is use_case2

    def test_factory_handles_sequential_requests_for_different_channels(self, mock_email_use_case, mock_web_use_case):
        factory = SendNotificationUseCaseFactory(mock_email_use_case, mock_web_use_case)
        email_use_case = factory.get_use_case(NotificationChannelsEnum.EMAIL)
        web_use_case = factory.get_use_case(NotificationChannelsEnum.WEB)
        assert email_use_case == mock_email_use_case
        assert web_use_case == mock_web_use_case
        assert email_use_case is not web_use_case

