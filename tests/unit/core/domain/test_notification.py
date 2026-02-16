"""Testes unitários para Notification domain entity"""
import pytest
from datetime import datetime, UTC
from uuid import UUID, uuid4
from core.domain.notification import EmailPayload, WebPayload, NotificationContent, Notification
from core.domain.vdsc_metadata import VdscMetadata
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO
from core.enums.email_template_enum import EmailTemplateEnum
from core.enums.notification_channels_enum import NotificationChannelsEnum


@pytest.mark.unit
class TestEmailPayload:
    """Testes para EmailPayload"""

    def test_valid_email_payload_created_successfully(self):
        email = EmailPayload(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        assert email.user_id == "user123"
        assert email.template == EmailTemplateEnum.UPDATE_STATUS

    def test_email_payload_with_failed_template_created_successfully(self):
        email = EmailPayload(
            user_id="user456",
            template=EmailTemplateEnum.FAILED
        )
        assert email.user_id == "user456"
        assert email.template == EmailTemplateEnum.FAILED

    def test_email_payload_with_finished_template_created_successfully(self):
        email = EmailPayload(
            user_id="user789",
            template=EmailTemplateEnum.FINISHED
        )
        assert email.template == EmailTemplateEnum.FINISHED


@pytest.mark.unit
class TestWebPayload:
    """Testes para WebPayload"""

    def test_valid_web_payload_created_successfully(self):
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayload(
            user_id="user123",
            message="Processamento concluído",
            timestamp=timestamp
        )
        assert web.user_id == "user123"
        assert web.message == "Processamento concluído"
        assert web.timestamp == timestamp

    def test_web_payload_with_different_timestamp_created_successfully(self):
        timestamp = datetime(2026, 3, 15, 18, 30, 45, tzinfo=UTC)
        web = WebPayload(
            user_id="user789",
            message="Nova notificação",
            timestamp=timestamp
        )
        assert web.timestamp == timestamp


@pytest.mark.unit
class TestNotificationContent:
    """Testes para NotificationContent"""

    def test_notification_content_with_email_only_created_successfully(self):
        email = EmailPayload(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        content = NotificationContent(email=email)
        assert content.email is not None
        assert content.web is None
        assert content.email.user_id == "user123"

    def test_notification_content_with_web_only_created_successfully(self):
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayload(
            user_id="user456",
            message="Teste",
            timestamp=timestamp
        )
        content = NotificationContent(web=web)
        assert content.web is not None
        assert content.email is None
        assert content.web.user_id == "user456"

    def test_notification_content_with_both_payloads_created_successfully(self):
        email = EmailPayload(
            user_id="user123",
            template=EmailTemplateEnum.FINISHED
        )
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayload(
            user_id="user123",
            message="Concluído",
            timestamp=timestamp
        )
        content = NotificationContent(email=email, web=web)
        assert content.email is not None
        assert content.web is not None
        assert content.email.user_id == content.web.user_id

    def test_empty_notification_content_created_successfully(self):
        content = NotificationContent()
        assert content.email is None
        assert content.web is None


@pytest.mark.unit
class TestNotification:
    """Testes para Notification domain entity"""

    @pytest.fixture
    def valid_metadata(self):
        """Fixture com metadados válidos"""
        dto = VdscMetadataDTO(
            video_id="video123",
            file_name="test_video.mp4",
            file_extension="mp4",
            status="UPLOADED",
            created="2026-01-13T00:00:00Z",
            user_id="user123",
            total_time=3600,
            unit_time="s",
            start_time=0,
            end_time=60,
            interval_time=["00:00:00", "00:01:00"],
            max_retries=3,
            retries=0,
            resize="high",
            quality_output_level=85,
            logs=[]
        )
        return VdscMetadata(dto=dto)

    def test_notification_with_email_channel_created_successfully(self, valid_metadata):
        email = EmailPayload(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        content = NotificationContent(email=email)
        notification = Notification(
            id=uuid4(),
            channels=[NotificationChannelsEnum.EMAIL],
            metadata=valid_metadata,
            content=[content]
        )
        assert notification.id is not None
        assert isinstance(notification.id, UUID)
        assert NotificationChannelsEnum.EMAIL in notification.channels
        assert len(notification.content) == 1

    def test_notification_with_web_channel_created_successfully(self, valid_metadata):
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayload(
            user_id="user123",
            message="Teste",
            timestamp=timestamp
        )
        content = NotificationContent(web=web)
        notification = Notification(
            id=uuid4(),
            channels=[NotificationChannelsEnum.WEB],
            metadata=valid_metadata,
            content=[content]
        )
        assert NotificationChannelsEnum.WEB in notification.channels
        assert notification.content[0].web is not None

    def test_notification_with_multiple_channels_created_successfully(self, valid_metadata):
        email = EmailPayload(
            user_id="user123",
            template=EmailTemplateEnum.FINISHED
        )
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayload(
            user_id="user123",
            message="Concluído",
            timestamp=timestamp
        )
        content = NotificationContent(email=email, web=web)
        notification = Notification(
            id=uuid4(),
            channels=[NotificationChannelsEnum.EMAIL, NotificationChannelsEnum.WEB],
            metadata=valid_metadata,
            content=[content]
        )
        assert len(notification.channels) == 2
        assert NotificationChannelsEnum.EMAIL in notification.channels
        assert NotificationChannelsEnum.WEB in notification.channels

    def test_notification_without_required_email_payload_raises_error(self, valid_metadata):
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayload(
            user_id="user123",
            message="Teste",
            timestamp=timestamp
        )
        content = NotificationContent(web=web)
        with pytest.raises(ValueError, match="Canal EMAIL requer EmailPayload"):
            Notification(
                id=uuid4(),
                channels=[NotificationChannelsEnum.EMAIL],
                metadata=valid_metadata,
                content=[content]
            )

    def test_notification_without_required_web_payload_raises_error(self, valid_metadata):
        email = EmailPayload(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        content = NotificationContent(email=email)
        with pytest.raises(ValueError, match="Canal WEB requer WebPayload"):
            Notification(
                id=uuid4(),
                channels=[NotificationChannelsEnum.WEB],
                metadata=valid_metadata,
                content=[content]
            )

    def test_notification_with_multiple_contents_created_successfully(self, valid_metadata):
        email1 = EmailPayload(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        email2 = EmailPayload(
            user_id="user456",
            template=EmailTemplateEnum.FINISHED
        )
        content1 = NotificationContent(email=email1)
        content2 = NotificationContent(email=email2)
        notification = Notification(
            id=uuid4(),
            channels=[NotificationChannelsEnum.EMAIL],
            metadata=valid_metadata,
            content=[content1, content2]
        )
        assert len(notification.content) == 2
        assert notification.content[0].email.user_id == "user123"
        assert notification.content[1].email.user_id == "user456"

    def test_notification_channels_validation_called_on_creation(self, valid_metadata):
        email = EmailPayload(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        content = NotificationContent(email=email)
        notification = Notification(
            id=uuid4(),
            channels=[NotificationChannelsEnum.EMAIL],
            metadata=valid_metadata,
            content=[content]
        )
        assert notification is not None

    def test_notification_with_empty_channels_list_created_successfully(self, valid_metadata):
        content = NotificationContent()
        notification = Notification(
            id=uuid4(),
            channels=[],
            metadata=valid_metadata,
            content=[content]
        )
        assert len(notification.channels) == 0

