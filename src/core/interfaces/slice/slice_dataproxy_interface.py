import datetime
from abc import ABC, abstractmethod

from core.dtos.notification_dto import NotificationDto
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO


class SliceDataProxyInterface(ABC):

    @abstractmethod
    def delete_file(self, file_path: str) -> None:
        pass

    @abstractmethod
    def delete_temp_files(self, tmp_path:str) -> None:
        pass

    @abstractmethod
    def open_file(self, file_path: str) -> bytes:
        pass

    @abstractmethod
    def save_file(self, file_path: str, data: bytes) -> None:
        pass

    @abstractmethod
    def send_metric(self, metric_info: str) -> None:
        pass

    @abstractmethod
    def send_notification(self, notification: NotificationDto) -> None:
        pass

    @abstractmethod
    def send_schedule_retry_event(self, vdsc_metadata: VdscMetadataDTO, schedule_time: datetime, schedule_config: dict) -> None:
        pass

    @abstractmethod
    def upload_finished_zip(self, output_directory: str, target_path: str) -> None:
        pass

    @abstractmethod
    def update_metadata_by_video_id(self, update_data: VdscMetadataDTO) -> VdscMetadataDTO:
        pass



