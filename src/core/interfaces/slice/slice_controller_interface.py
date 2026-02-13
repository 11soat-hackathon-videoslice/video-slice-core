from abc import ABC, abstractmethod

from core.dtos.vdsc_config_dto import VdscConfigDTO
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO


class SliceControllerInterface(ABC):

        @abstractmethod
        def video_slice_processing(self, event: VdscMetadataDTO, config: VdscConfigDTO) -> dict:
            pass