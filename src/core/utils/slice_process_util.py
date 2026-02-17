import logging
import os
import queue
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Optional
from uuid import uuid4

import cv2
import time

from core.interfaces import SliceGatewayInferface
from .schedule_event_util import get_event_schedule_timestamp
from .slice_video_process_frame_util import process_video_frame
from ..domain.notification import EmailPayload, WebPayload, Notification, NotificationContent
from ..domain.vdsc_metadata import VdscMetadata, LogEntry
from ..dtos.vdsc_config_dto import VdscConfigDTO
from ..enums.email_template_enum import EmailTemplateEnum
from ..enums.notification_channels_enum import NotificationChannelsEnum
from ..enums.vdsc_status_enum import VdscStatusEnum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_email_notification(metadata: VdscMetadata, email_template: EmailTemplateEnum) -> EmailPayload:
    """Cria payload de notificação por email"""
    return EmailPayload(
        user_id=metadata.user_id,
        template=email_template
    )

def create_interval_list(vdsc_metadata, time_unit_multiplier):
    """Cria lista de intervalos de tempo para extração de frames"""
    start_time = int(vdsc_metadata.start_time * time_unit_multiplier)
    logger.info(f"start_time: {start_time}")
    end_time = int(vdsc_metadata.end_time * time_unit_multiplier)
    logger.info(f"end_time: {end_time}")
    interval = int(vdsc_metadata.interval_time[0]) * int(time_unit_multiplier)
    logger.info(f"interval: {interval}")

    if len(vdsc_metadata.interval_time) == 1:
        interval_time_list = get_recurrent_interval_times(start_time, end_time, interval)
    else:
        interval_time_list = get_specific_interval_times(vdsc_metadata.interval_time, int(time_unit_multiplier))
    return interval_time_list

def create_notification(metadata: VdscMetadata, channels: list[str],
                        web_message: Optional[str] = None,
                        email_template: Optional[EmailTemplateEnum] = None) -> Notification:
    """Cria notificação com payloads de email e web"""
    content = []
    # Cria conteúdo apenas se houver dados
    if email_template or web_message:
        content.append(NotificationContent(
            email=create_email_notification(metadata, email_template) if email_template else None,
            web=create_web_notification(metadata, web_message) if web_message else None
        ))

    return Notification(
        id=uuid4(),
        metadata=metadata,
        channels=[NotificationChannelsEnum[ch.upper()] for ch in channels],
        content=content
    )

def create_temporary_file(video_data, file_extension) -> str:
    """Cria arquivo temporário com os dados do vídeo"""
    with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as temp_file:
        temp_file.write(video_data)
        temp_file_path = temp_file.name
    return temp_file_path

def create_web_notification(metadata: VdscMetadata, message: str) -> WebPayload:
    """Cria payload de notificação web"""
    return WebPayload(
        user_id=metadata.user_id,
        message=message,
        timestamp=datetime.now()
    )

def get_multiplier_time_unit(time_unit: str) -> int:
    """Retorna multiplicador para conversão de unidade de tempo"""
    return 1000 if time_unit == 's' else 1


def get_path_file(prefix_path: str, file_name: str, file_extension) -> str:
    """Retorna o caminho completo do arquivo"""
    return f"{prefix_path}/{file_name}.{file_extension}"


def get_path_directory(prefix_path: str, video_id) -> str:
    """Retorna o caminho completo do diretório"""
    return f"{prefix_path}/{video_id}/"


def get_recurrent_interval_times(start_time: int, end_time: int, interval: int):
    """Gera lista de intervalos de tempo recorrentes"""
    logger.info("Gerando intervalos de tempo recorrentes")
    current_time = start_time
    interval_time_list = []
    while current_time <= end_time:
        interval_time_list.append(current_time)
        current_time += interval
    logger.info(f"interval_time_list: {interval_time_list}")
    return interval_time_list


def get_specific_interval_times(interval_times, multiplier: int) -> list[int]:
    """Converte intervalos de tempo específicos para milissegundos"""
    logger.info("Convertendo intervalos de tempo específicos para milissegundos")
    return [int(time) * int(multiplier) for time in interval_times]


def get_frame_new_size(frame, target_frame_min_size: int) -> tuple[int, int, int]:
    """Calcula a proporção de redimensionamento do frame e retorna a largura alvo mantendo a proporção"""
    #Busca tamanho original do frame
    original_height, original_width = frame.shape[:2]
    # Busca menor dimensão do frame original para calcular proporção de redimensionamento
    original_min_size = min(original_height, original_width)
    #Calcula proporção de redimensionamento com base na menor dimensão do frame original e no tamanho mínimo desejado
    ratio = target_frame_min_size / original_min_size
    #Valida se a largura é maior que altura
    if original_width > original_height:
        # Cenário landscape: a altura é a dimensão limitante, então calcula nova largura mantendo proporção.
        return int(original_width * ratio), target_frame_min_size, original_min_size
    else:
        # Cenário portrait: a largura é a dimensão limitante, então calcula nova altura mantendo proporção.
        return target_frame_min_size, int(original_height * ratio), original_min_size


def metadata_update_status(vdsc_metadata: VdscMetadata, new_status: VdscStatusEnum, log: LogEntry) -> VdscMetadata:
    """Atualiza status e adiciona log aos metadados"""
    vdsc_metadata.status = new_status.value
    vdsc_metadata.logs.append(log)
    return vdsc_metadata

def process_video(vdsc_metadata: VdscMetadata, video_data, video_output_directory, gateway, config: VdscConfigDTO):
    """Processa os frames do vídeo e salva as imagens"""
    #Inicializando variáveis
    resize_params = {'resize':None, 'new_width':None, 'new_height':None, 'original_min_size': None}
    max_workers = int(config.vdsc.max_workers)

    video_id = vdsc_metadata.video_id
    logger.debug(f"video_id: {video_id}")

    time_unit_multiplier = get_multiplier_time_unit(vdsc_metadata.unit_time)
    logger.debug(f"time_unit_multiplier: {time_unit_multiplier}")

    video_temp_path = create_temporary_file(video_data, vdsc_metadata.file_extension)
    logger.debug(f"video_temp_path: {video_temp_path}")

    output_quality = vdsc_metadata.resize
    logger.debug(f"output_quality: {vdsc_metadata.resize}:{output_quality}")

    interval_list = create_interval_list(vdsc_metadata, time_unit_multiplier)

    try:
        resize_params = _check_resizer_needed(getattr(config.vdsc.resize, output_quality, None),video_temp_path)


        save_queue = queue.Queue(maxsize=max_workers * 2) # Capacidade maior para não gerar gargalo de I/O
        save_file_thread = threading.Thread(target=_save_frames_from_queue, args=(gateway, save_queue), daemon=True)
        save_file_thread.start()

        start_total = time.perf_counter()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_video_frame,
                                   interval,
                                    video_temp_path,
                                    resize_params,
                                   vdsc_metadata,
                                   video_output_directory,
                                   output_quality,
                                   video_id,
                                   time_unit_multiplier)
                                   for interval in interval_list
                       ]
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if save_queue.full():
                        logger.warning("ALERTA: Fila de escrita cheia!")
                    save_queue.put(result)
                except Exception as e:
                    logger.error(f"Erro ao processar frame: {str(e)}", exc_info=True)

        save_queue.join()
        save_queue.put(None)
        save_file_thread.join()
        total_duration  = time.perf_counter() - start_total
        avg_time_per_frame = total_duration / len(interval_list)
        metric_info = _set_metric_info(video_temp_path, vdsc_metadata.quality_output_level , resize_params, interval_list, total_duration, avg_time_per_frame, max_workers)
        gateway.send_metric(metric_info)
        logger.debug(f"{vdsc_metadata.video_id} - Tempo total de execução: {total_duration:.2f} segundos")
        logger.debug(f"{vdsc_metadata.video_id} - Eficiência Média por frame: {avg_time_per_frame:.2f} segundos")

    except Exception as e:
        logger.error(f"Erro ao processar frames do vídeo ID {video_id}: {str(e)}", exc_info=e)
        raise


def set_exception_status(gateway: SliceGatewayInferface, ex: Exception, vdsc_metadata: VdscMetadata, new_status: VdscStatusEnum, config: VdscConfigDTO):
    match new_status:
        case VdscStatusEnum.FAILED:
            return set_exception_status_failed(gateway, ex, vdsc_metadata, new_status)
        case VdscStatusEnum.RETRYING:
            return set_exception_status_retrying(gateway, ex, vdsc_metadata, config, new_status)
    return None

def set_exception_status_failed(gateway: SliceGatewayInferface, ex: Exception, vdsc_metadata: VdscMetadata, new_status: VdscStatusEnum):
    message = f" {vdsc_metadata.video_id} - Processamento do video {vdsc_metadata.file_name}.{vdsc_metadata.file_extension} falhou após {vdsc_metadata.max_retries} tentativas: {str(ex)}."
    vdsc_metadata = metadata_update_status(vdsc_metadata, new_status, LogEntry(f"Processamento falhou após {vdsc_metadata.max_retries} tentativas."))
    gateway.send_notification(create_notification(vdsc_metadata, ['web','email'], message, EmailTemplateEnum.FAILED))
    return vdsc_metadata, message

def set_exception_status_retrying(gateway: SliceGatewayInferface, ex: Exception, vdsc_metadata: VdscMetadata, config: VdscConfigDTO, new_status: VdscStatusEnum):
    """Define status como RETRYING e agenda nova tentativa"""
    vdsc_metadata.retries += 1
    schedule_timestamp = get_event_schedule_timestamp(vdsc_metadata, retry_backoff_factor = config.vdsc.schedule_event_rules.retry_backoff_factor)
    message = f"{vdsc_metadata.video_id} - Falha no processamento do video {vdsc_metadata.file_name}.{vdsc_metadata.file_extension}. Tentativa {vdsc_metadata.retries} de {vdsc_metadata.max_retries} agendada para {_print_schedule_brasil(schedule_timestamp)}."
    vdsc_metadata = metadata_update_status(vdsc_metadata, new_status, LogEntry(f"{message}{str(ex)}"))
    gateway.send_schedule_retry_event(vdsc_metadata, schedule_timestamp, config.vdsc.schedule_event_rules.to_dict())
    gateway.send_notification(create_notification(vdsc_metadata, ['web','email'], message, EmailTemplateEnum.PROCESSING))
    return vdsc_metadata, message

def _check_resizer_needed(min_size: int, video_temp_path: str) -> dict:
    vidcap_check = cv2.VideoCapture(video_temp_path)
    #Obtendo primeiro frame do video para obter dimensões atuais
    vidcap_check.set(cv2.CAP_PROP_POS_MSEC, 1)
    _, frame = vidcap_check.read()
    original_min_size = min(frame.shape[:2])
    resize_params = {'resize': None, 'new_width': None, 'new_height': None, 'original_min_size': original_min_size}

    if min_size:
        logger.info("Nenhum redimensionamento configurado.")
        new_width, new_height, original_min_size = get_frame_new_size(frame, min_size)
        resize_params = {'resize':True, 'new_width':new_width, 'new_height':new_height, 'original_min_size': original_min_size}
        logger.info(f"Configurações de redimensionamento: {resize_params}")

    vidcap_check.release()
    return resize_params

def _print_schedule_brasil(schedule_time: datetime):
    from datetime import timedelta, timezone
    # Converte de UTC para o fuso de Brasília (UTC-3)
    fuso_brasilia = timezone(timedelta(hours=-3))
    horario_brasil = schedule_time.astimezone(fuso_brasilia)
    # Formata no padrão brasileiro
    return horario_brasil.strftime('%d/%m/%Y %H:%M')

def _save_frames_from_queue(gateway: SliceGatewayInferface, save_queue: queue.Queue):
    while True:
        result = save_queue.get()
        if result is None:
            break
        try:
            if result.get("success") and result.get("data"):
                # Salva o arquivo localmente
                gateway.save_file(result.get("file_output"), result.get("data"))
                logger.debug(f"Frame salvo com sucesso: {result.get('file_output')}")
        except Exception as e:
            logger.error(f"Erro ao salvar frame: {str(e)}", exc_info=True)
        finally:
            save_queue.task_done()

def _set_metric_info(video_temp_path: str, quality_output_level: str, resize_params: dict, interval_time: list,
                    process_total_time: float, avg_time_per_frame: float, max_workers: int) -> dict:


    return {
        'resize': resize_params['resize'] if resize_params['resize'] is not None else False,
        'original_min_size': resize_params['original_min_size'],
        'resize_output': min(resize_params['new_width'], resize_params['new_height']) if resize_params['new_width'] is not None and resize_params['new_height'] is not None else None,
        'quality_output_level': quality_output_level,
        'frames_processed': len(interval_time),
        'workers': max_workers,
        'video_size_mb': round(os.path.getsize(video_temp_path) / (1024 * 1024), 2),
        'process_total_time_seconds': process_total_time,
        'efficiency_per_frame_seconds': avg_time_per_frame
    }