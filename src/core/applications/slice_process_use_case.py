import logging

from core.interfaces import SliceGatewayInferface
from ..dtos.vdsc_metadata_dto import VdscMetadataDTO
from ..dtos.vdsc_config_dto import VdscConfigDTO
from ..domain.vdsc_metadata import VdscMetadata, LogEntry
from ..enums.vdsc_status_enum import VdscStatusEnum
from ..exceptions.vdsc_exceptions import VdscException
from core.interfaces import VdscExceptionHandlerInterface
from ..utils.slice_process_util import (
    compress_images_to_zip,
    get_path_file,
    get_path_directory,
    process_video_frames,
    metadata_update_status,
    set_exception_status
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SliceProcessUseCase:

    def execute(self, gateway: SliceGatewayInferface, event: VdscMetadataDTO, config: VdscConfigDTO, handler: VdscExceptionHandlerInterface):
        """Executa o processamento de vídeo com tratamento de exceções via handler injetado"""
        logger.info(f"Iniciando o caso de uso de processamento de vídeo para o vídeo ID: {event.video_id}")

        #Construindo entidade de domínio a partir do DTO
        vdsc_metadata = VdscMetadata(dto=event)
        video_id = vdsc_metadata.video_id
        retries = vdsc_metadata.retries
        max_retries = vdsc_metadata.max_retry
        extension_file = vdsc_metadata.extension_file

        try:
            # Atualizando status de metadados para Processing ou Retrying
            if vdsc_metadata.status.upper() == VdscStatusEnum.UPLOADED.value.upper():
                vdsc_metadata = metadata_update_status(vdsc_metadata, VdscStatusEnum.PROCESSING, LogEntry(f"Iniciando processamento do vídeo: {video_id}"))
            elif vdsc_metadata.status.upper() == VdscStatusEnum.RETRYING.value.upper():
                retries += 1
                vdsc_metadata.retries = retries
                log_message = f"Reiniciando processamento do vídeo: {video_id}. Tentativa {retries} de {max_retries}."
                vdsc_metadata = metadata_update_status(vdsc_metadata, VdscStatusEnum.RETRYING, LogEntry(log_message))
            gateway.update_metadata(vdsc_metadata)

            # Movendo arquivo para área de processamento
            file_uploaded_path = get_path_file(prefix_path=config.s3_bucket.dir_uploads, video_id=video_id, extension_file=extension_file)
            file_processing_path = get_path_file(prefix_path=config.s3_bucket.dir_processing, video_id=video_id, extension_file=extension_file)
            gateway.move_file(file_uploaded_path, file_processing_path)

            #Criando diretório para imagens processadas
            video_output_directory = get_path_directory(prefix_path=config.s3_bucket.dir_processing, video_id=video_id)
            gateway.create_directory(video_output_directory)

            #Abrindo arquivo de video para processamento
            video_data = gateway.open_file(file_processing_path)

            #Processamento de caputura de frames
            logger.info(f"Iniciando captura de imagens para o vídeo ID: {event.video_id}")
            process_video_frames(video_id, vdsc_metadata, video_data, video_output_directory, gateway, config)
            logger.info(f"Finalizada captura de imagens para o vídeo ID: {event.video_id})")

            #Compactando arquivos para zip
            zip_output_path = get_path_file(config.s3_bucket.dir_finished, video_id=video_id, extension_file='zip')
            compress_images_to_zip(video_output_directory, zip_output_path, gateway, config)

            #Deletando diretório de imagens processadas
            gateway.delete_files_by_directory(video_output_directory)

            #Deletando video processado
            gateway.delete_file(file_processing_path)

            #Atualizando metadados para finalizado
            vdsc_metadata = metadata_update_status(vdsc_metadata, VdscStatusEnum.FINISHED, LogEntry("Processamento finalizado com sucesso."))
            gateway.update_metadata(vdsc_metadata)

            logger.info(f"Processamento concluído com sucesso para o vídeo ID: {event.video_id}")

        except Exception as ex:
            logger.error(f"Erro ao processar o vídeo ID {event.video_id}: {str(ex)}", exc_info=ex)

            if retries == max_retries:
                vdsc_metadata_error, message = set_exception_status(gateway, ex, vdsc_metadata, VdscStatusEnum.FAILED, config)
            else:
                vdsc_metadata_error, message = set_exception_status(gateway, ex, vdsc_metadata, VdscStatusEnum.RETRYING, config)

            if vdsc_metadata_error:
                vdsc_metadata = vdsc_metadata_error
                gateway.update_metadata(vdsc_metadata_error)
                gateway.send_notification(vdsc_metadata_error, ['email'], message)
            raise VdscException(message, "ERROR", vdsc_metadata_error.to_dict())

