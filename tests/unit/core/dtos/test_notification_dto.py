"""Testes unitários para NotificationDto"""
import pytest
from datetime import datetime, UTC
from uuid import uuid4
from core.dtos.notification_dto import EmailPayloadDto, WebPayloadDto, NotificationContentDto, NotificationDto
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO
from core.enums.email_template_enum import EmailTemplateEnum
from core.enums.notification_channels_enum import NotificationChannelsEnum


@pytest.mark.unit
class TestEmailPayloadDto:
    """Testes para EmailPayloadDto"""

    def test_valid_email_payload_created_successfully(self):
        email_payload = EmailPayloadDto(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        assert email_payload.user_id == "user123"
        assert email_payload.template == EmailTemplateEnum.UPDATE_STATUS

    def test_email_payload_converted_to_dict_correctly(self):
        email_payload = EmailPayloadDto(
            user_id="user123",
            template=EmailTemplateEnum.FAILED
        )
        result = email_payload.to_dict()
        assert result["user_id"] == "user123"
        assert result["template"] == "FAILED"

    def test_email_payload_with_finished_template_converted_correctly(self):
        email_payload = EmailPayloadDto(
            user_id="user456",
            template=EmailTemplateEnum.FINISHED
        )
        result = email_payload.to_dict()
        assert result["user_id"] == "user456"
        assert result["template"] == "FINISHED"


@pytest.mark.unit
class TestWebPayloadDto:
    """Testes para WebPayloadDto"""

    def test_valid_web_payload_created_successfully(self):
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web_payload = WebPayloadDto(
            user_id="user123",
            message="Processamento concluído",
            timestamp=timestamp,
            is_read=False
        )
        assert web_payload.user_id == "user123"
        assert web_payload.message == "Processamento concluído"
        assert web_payload.timestamp == timestamp
        assert web_payload.is_read is False

    def test_web_payload_converted_to_dict_correctly(self):
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web_payload = WebPayloadDto(
            user_id="user123",
            message="Teste mensagem",
            timestamp=timestamp,
            is_read=True
        )
        result = web_payload.to_dict()
        assert result["user_id"] == "user123"
        assert result["message"] == "Teste mensagem"
        assert result["timestamp"] == "2026-02-08T12:00:00+00:00"
        assert result["is_read"] is True

    def test_web_payload_with_unread_status_converted_correctly(self):
        timestamp = datetime(2026, 1, 13, 0, 0, 0, tzinfo=UTC)
        web_payload = WebPayloadDto(
            user_id="user789",
            message="Nova notificação",
            timestamp=timestamp,
            is_read=False
        )
        result = web_payload.to_dict()
        assert result["is_read"] is False


@pytest.mark.unit
class TestNotificationContentDto:
    """Testes para NotificationContentDto"""

    def test_notification_content_with_email_only_created_successfully(self):
        email = EmailPayloadDto(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        content = NotificationContentDto(email=email)
        assert content.email is not None
        assert content.web is None
        assert content.email.user_id == "user123"

    def test_notification_content_with_web_only_created_successfully(self):
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayloadDto(
            user_id="user456",
            message="Teste",
            timestamp=timestamp,
            is_read=False
        )
        content = NotificationContentDto(web=web)
        assert content.web is not None
        assert content.email is None
        assert content.web.user_id == "user456"

    def test_notification_content_with_both_payloads_created_successfully(self):
        email = EmailPayloadDto(
            user_id="user123",
            template=EmailTemplateEnum.FINISHED
        )
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayloadDto(
            user_id="user123",
            message="Concluído",
            timestamp=timestamp,
            is_read=False
        )
        content = NotificationContentDto(email=email, web=web)
        assert content.email is not None
        assert content.web is not None

    def test_notification_content_with_email_converted_to_dict_correctly(self):
        email = EmailPayloadDto(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        content = NotificationContentDto(email=email)
        result = content.to_dict()
        assert result["email"] is not None
        assert result["email"]["user_id"] == "user123"
        assert result["web"] is None

    def test_notification_content_with_web_converted_to_dict_correctly(self):
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayloadDto(
            user_id="user456",
            message="Teste",
            timestamp=timestamp,
            is_read=True
        )
        content = NotificationContentDto(web=web)
        result = content.to_dict()
        assert result["web"] is not None
        assert result["web"]["user_id"] == "user456"
        assert result["email"] is None

    def test_empty_notification_content_converted_to_dict_with_none_values(self):
        content = NotificationContentDto()
        result = content.to_dict()
        assert result["email"] is None
        assert result["web"] is None


@pytest.mark.unit
class TestNotificationDto:
    """Testes para NotificationDto"""

    @pytest.fixture
    def valid_metadata_dto(self):
        """Fixture com metadados válidos"""
        return VdscMetadataDTO(
            video_id="video123",
            file_name="test_video.mp4",
            extension_file="mp4",
            status="UPLOADED",
            created="2026-01-13T00:00:00Z",
            user_id="user123",
            total_time=3600,
            unit_time="s",
            start_time=0,
            end_time=60,
            time_interval=["00:00:00", "00:01:00"],
            max_retry=3,
            retries=0,
            quality="high",
            logs=[]
        )

    def test_notification_with_email_channel_created_successfully(self, valid_metadata_dto):
        email = EmailPayloadDto(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        content = NotificationContentDto(email=email)
        notification = NotificationDto(
            id=str(uuid4()),
            channels=[NotificationChannelsEnum.EMAIL],
            metadata=valid_metadata_dto,
            content=[content]
        )
        assert notification.id is not None
        assert NotificationChannelsEnum.EMAIL in notification.channels
        assert len(notification.content) == 1

    def test_notification_with_web_channel_created_successfully(self, valid_metadata_dto):
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayloadDto(
            user_id="user123",
            message="Teste",
            timestamp=timestamp,
            is_read=False
        )
        content = NotificationContentDto(web=web)
        notification = NotificationDto(
            id=str(uuid4()),
            channels=[NotificationChannelsEnum.WEB],
            metadata=valid_metadata_dto,
            content=[content]
        )
        assert NotificationChannelsEnum.WEB in notification.channels

    def test_notification_with_multiple_channels_created_successfully(self, valid_metadata_dto):
        email = EmailPayloadDto(
            user_id="user123",
            template=EmailTemplateEnum.FINISHED
        )
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayloadDto(
            user_id="user123",
            message="Concluído",
            timestamp=timestamp,
            is_read=False
        )
        content = NotificationContentDto(email=email, web=web)
        notification = NotificationDto(
            id=str(uuid4()),
            channels=[NotificationChannelsEnum.EMAIL, NotificationChannelsEnum.WEB],
            metadata=valid_metadata_dto,
            content=[content]
        )
        assert len(notification.channels) == 2
        assert NotificationChannelsEnum.EMAIL in notification.channels
        assert NotificationChannelsEnum.WEB in notification.channels

    def test_notification_without_required_email_payload_raises_error(self, valid_metadata_dto):
        timestamp = datetime(2026, 2, 8, 12, 0, 0, tzinfo=UTC)
        web = WebPayloadDto(
            user_id="user123",
            message="Teste",
            timestamp=timestamp,
            is_read=False
        )
        content = NotificationContentDto(web=web)
        with pytest.raises(ValueError, match="Canal EMAIL requer EmailPayload"):
            notification = NotificationDto(
                id=str(uuid4()),
                channels=[NotificationChannelsEnum.EMAIL],
                metadata=valid_metadata_dto,
                content=[content]
            )
            notification._validate_channels()

    def test_notification_without_required_web_payload_raises_error(self, valid_metadata_dto):
        email = EmailPayloadDto(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        content = NotificationContentDto(email=email)
        with pytest.raises(ValueError, match="Canal WEB requer WebPayload"):
            notification = NotificationDto(
                id=str(uuid4()),
                channels=[NotificationChannelsEnum.WEB],
                metadata=valid_metadata_dto,
                content=[content]
            )
            notification._validate_channels()

    def test_notification_converted_to_dict_correctly(self, valid_metadata_dto):
        email = EmailPayloadDto(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        content = NotificationContentDto(email=email)
        notification_id = str(uuid4())
        notification = NotificationDto(
            id=notification_id,
            channels=[NotificationChannelsEnum.EMAIL],
            metadata=valid_metadata_dto,
            content=[content]
        )
        result = notification.to_dict()
        assert result["id"] == notification_id
        assert "EMAIL" in result["channels"]
        assert result["metadata"] is not None
        assert len(result["content"]) == 1

    def test_notification_with_multiple_contents_converted_correctly(self, valid_metadata_dto):
        email1 = EmailPayloadDto(
            user_id="user123",
            template=EmailTemplateEnum.UPDATE_STATUS
        )
        email2 = EmailPayloadDto(
            user_id="user456",
            template=EmailTemplateEnum.FINISHED
        )
        content1 = NotificationContentDto(email=email1)
        content2 = NotificationContentDto(email=email2)
        notification = NotificationDto(
            id=str(uuid4()),
            channels=[NotificationChannelsEnum.EMAIL],
            metadata=valid_metadata_dto,
            content=[content1, content2]
        )
        result = notification.to_dict()
        assert len(result["content"]) == 2

