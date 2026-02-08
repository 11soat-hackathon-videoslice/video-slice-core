import logging

from core.domain.url import Url
from core.dtos.url_dto import UrlRequestDto
from core.interfaces import UrlGatewayInterface
from core.exceptions.vdsc_exceptions import VdscException
from core.enums.vdsc_status_enum import VdscStatusEnum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeneratePresignedURLUseCase:
    def __init__(self, gateway: UrlGatewayInterface):
        self.gateway = gateway

    def execute(self, request: UrlRequestDto) -> Url:
        try:
            url_request = Url.from_request(request)

            if request.action == "upload":
                return self.gateway.generate_upload_presigned_url(url_request)
            elif request.action == "download":
                return self.gateway.generate_download_presigned_url(url_request)
            else:
                raise ValueError(f"Operação não suportada: {request.action}")

        except Exception as e:
            logger.error(f"Erro ao gerar URL presigned: {e}", exc_info=True)
            raise VdscException(f"Falha ao gerar URL presigned: {str(e)}", VdscStatusEnum.ERROR, request.to_dict())



