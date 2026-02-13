import datetime

from core.domain.notification import Notification
from core.dtos.notification_dto import NotificationDto
from core.interfaces import SliceGatewayInferface
from core.interfaces import SliceDataProxyInterface
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO
from core.domain.vdsc_metadata import VdscMetadata

class SliceGateway(SliceGatewayInferface):

    def __init__(self, dataproxy: SliceDataProxyInterface):
        self.dataproxy = dataproxy

    def create_zip_file(self, directory_path: str, zip_file_path: str) -> None:
        self.dataproxy.create_zip_file(directory_path, zip_file_path)

    def delete_file(self, file_path: str) -> None:
        self.dataproxy.delete_file(file_path)

    def delete_temp_files(self, tmp_path:str) -> None:
        self.dataproxy.delete_temp_files(tmp_path)

    def open_file(self, file_path: str) -> bytes:
        return self.dataproxy.open_file(file_path)

    def save_file(self, file_path: str, data: str) -> None:
        self.dataproxy.save_file(file_path, data)

    def save_file_local(self, file_path: str, data: bytes) -> None:
        self.dataproxy.save_file_local(file_path, data)

    def send_schedule_retry_event(self, vdsc_metadata: VdscMetadata, schedule_time: datetime, schedule_config: dict) -> None:
        event_metadata = VdscMetadataDTO.from_dict(vdsc_metadata.to_dict())
        self.dataproxy.send_schedule_retry_event(event_metadata, schedule_time, schedule_config)

    def send_notification(self, notification: Notification) -> None:
        notification_dto = NotificationDto.from_domain(notification)
        self.dataproxy.send_notification(notification_dto)

    def update_metadata(self, update_data: VdscMetadata) -> VdscMetadata:
        """Atualiza metadados convertendo a entidade de domínio para DTO"""
        # Converter entidade de domínio para dict e depois para DTO
        update_data_dto = VdscMetadataDTO.from_dict(update_data.to_dict())
        # Atualizar via dataproxy
        updated_dto = self.dataproxy.update_metadata_by_video_id(update_data_dto)
        # Converter DTO de volta para entidade de domínio
        return VdscMetadata(dto=updated_dto)

    def upload_zip_file(self, source_path: str, target_path: str) -> None:
        self.dataproxy.upload_zip_file(source_path, target_path)


