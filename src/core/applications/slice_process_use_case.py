import logging

from core.interfaces import SliceGatewayInferface
from core.interfaces import VdscExceptionHandlerInterface
from ..domain.vdsc_metadata import VdscMetadata, LogEntry
from ..dtos.vdsc_config_dto import VdscConfigDTO
from ..dtos.vdsc_metadata_dto import VdscMetadataDTO
from ..enums.email_template_enum import EmailTemplateEnum
from ..enums.vdsc_status_enum import VdscStatusEnum
from ..exceptions.vdsc_exceptions import VdscException
from ..utils.slice_process_util import (
    get_path_file,
    get_path_directory,
    process_video,
    metadata_update_status,
    set_exception_status,
    create_notification
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
        max_retries = vdsc_metadata.max_retries
        file_extension = vdsc_metadata.file_extension
        zip_name = f"{vdsc_metadata.file_name}_{vdsc_metadata.video_id}"
        video_name = f"{vdsc_metadata.file_name}.{file_extension}"
        log_message = None
        email_template_enum = None
        try:
            # Atualizando status de metadados para Processing ou Retrying
            if vdsc_metadata.status.upper() == VdscStatusEnum.UPLOADED.value.upper():
                log_message=f"{video_id} - Iniciando processamento do vídeo {video_name}"
                vdsc_metadata = metadata_update_status(vdsc_metadata, VdscStatusEnum.PROCESSING, LogEntry(log_message))
                email_template_enum = EmailTemplateEnum.PROCESSING
            elif vdsc_metadata.status.upper() == VdscStatusEnum.RETRYING.value.upper():
                vdsc_metadata.retries = retries
                log_message = f"{video_id} - Reiniciando processamento do vídeo: {video_name}. Tentativa {retries} de {max_retries}."
                email_template_enum = EmailTemplateEnum.PROCESSING
            gateway.update_metadata(vdsc_metadata)
            gateway.send_notification(create_notification(vdsc_metadata,['web','email'], log_message, email_template_enum))

            video_path = get_path_file(prefix_path=config.vdsc.dir_uploads, file_name=video_id, file_extension=file_extension)
            #Criando diretório para imagens processadas
            video_output_directory = get_path_directory(prefix_path=config.vdsc.dir_tmp, video_id=video_id)
            #Abrindo arquivo de video para processamento
            video_data = gateway.open_file(file_path=video_path)

            #Processamento de caputura de frames
            logger.info(f"Iniciando captura de imagens para o vídeo ID: {event.video_id}")
            process_video(vdsc_metadata, video_data, video_output_directory, gateway, config)
            logger.info(f"Finalizada captura de imagens para o vídeo ID: {event.video_id})")

            #Compactando arquivos para zip e fazendo upload para diretório final
            finished_zip_path = get_path_file(prefix_path=config.vdsc.dir_finished, file_name=zip_name, file_extension='zip')
            gateway.upload_finished_zip(output_directory=video_output_directory, target_path=finished_zip_path)

            #Deletando video processado
            gateway.delete_file(video_path)
            gateway.delete_temp_files(video_output_directory)

            #Atualizando metadados para finalizado
            log_message = f" {video_id} - Processamento do vídeo {video_name} finalizado com sucesso."
            vdsc_metadata = metadata_update_status(vdsc_metadata, VdscStatusEnum.FINISHED, LogEntry(log_message))
            gateway.update_metadata(vdsc_metadata)
            gateway.send_notification(create_notification(vdsc_metadata,['web','email'], log_message, EmailTemplateEnum.FINISHED))

            logger.info(f"Processamento concluído com sucesso para o vídeo ID: {event.video_id}")

        except Exception as ex:
            logger.error(f"{video_id} - Erro ao processar o vídeo {video_name}: {str(ex)}", exc_info=ex)
            if retries == max_retries:
                vdsc_metadata_error, message = set_exception_status(gateway, ex, vdsc_metadata, VdscStatusEnum.FAILED, config)
            else:
                vdsc_metadata_error, message = set_exception_status(gateway, ex, vdsc_metadata, VdscStatusEnum.RETRYING, config)
            gateway.update_metadata(vdsc_metadata_error)
            raise VdscException(message, "ERROR", vdsc_metadata_error.to_dict())
