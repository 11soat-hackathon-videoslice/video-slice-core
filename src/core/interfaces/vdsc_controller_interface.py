from abc import ABC, abstractmethod
from ..dtos.vdsc_metadata_dto import VdscMetadataDTO
from ..dtos.vdsc_config_dto import VdscConfigDTO

class VdscControllerInterface(ABC):

        @abstractmethod
        def video_slice_processing(self, event: VdscMetadataDTO, config: VdscConfigDTO) -> dict:
            pass