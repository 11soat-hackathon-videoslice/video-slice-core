from core.interfaces import SliceControllerInterface
from core.interfaces import SliceDataProxyInterface
from core.interfaces import VdscExceptionHandlerInterface
from core.dtos.vdsc_metadata_dto import VdscMetadataDTO
from core.dtos.vdsc_config_dto import VdscConfigDTO
from .slice_gateway import SliceGateway
from core.applications.slice_process_use_case import SliceProcessUseCase

class SliceController(SliceControllerInterface):

    def __init__(self, dataproxy: SliceDataProxyInterface, handler: VdscExceptionHandlerInterface):
        self.data_proxy = dataproxy
        self.handler = handler

    def video_slice_processing(self, event: VdscMetadataDTO, config: VdscConfigDTO) -> None:
        gateway = SliceGateway(self.data_proxy)
        use_case = SliceProcessUseCase()
        use_case.execute(gateway, event, config, self.handler)







