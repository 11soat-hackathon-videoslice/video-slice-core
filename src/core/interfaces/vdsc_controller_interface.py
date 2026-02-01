from abc import ABC, abstractmethod
from ..dtos.vdsc_metadata_dto import VdscMetadataDTO

class VdscControllerInterface(ABC):

        @abstractmethod
        def video_slice_processing(self, event: VdscMetadataDTO, config: dict) -> dict:
            pass