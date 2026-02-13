import datetime
from abc import ABC, abstractmethod

from core.domain.notification import Notification
from core.domain.vdsc_metadata import VdscMetadata

class SliceGatewayInferface(ABC):

    @abstractmethod
    def create_zip_file(self, directory_path: str, zip_file_path: str) -> None:
        pass

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
    def send_schedule_retry_event(self, vdsc_metadata: VdscMetadata, schedule_time: datetime, schedule_config: dict) -> None:
        pass

    @abstractmethod
    def send_notification(self, notification: Notification) -> None:
        pass

    @abstractmethod
    def update_metadata(self, update_data: VdscMetadata) -> VdscMetadata:
        pass

    @abstractmethod
    def upload_zip_file(self, directory_path: str, zip_file_path: str) -> None:
        pass




