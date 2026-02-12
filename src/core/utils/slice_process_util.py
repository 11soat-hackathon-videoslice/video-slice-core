import threading
from concurrent.futures.thread import ThreadPoolExecutor
from itertools import repeat
from typing import Optional
from datetime import datetime
from uuid import uuid4

import io
import logging
import tempfile
import zipfile

import cv2

from pathlib import Path
from core.interfaces import SliceGatewayInferface
from ..domain.notification import EmailPayload, WebPayload, Notification, NotificationContent
from ..dtos.vdsc_config_dto import VdscConfigDTO
from ..domain.vdsc_metadata import VdscMetadata, LogEntry
from ..enums.email_template_enum import EmailTemplateEnum
from ..enums.notification_channels_enum import NotificationChannelsEnum
from ..enums.vdsc_status_enum import VdscStatusEnum
from ..utils import get_event_schedule_timestamp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_email_notification(metadata: VdscMetadata, email_template: EmailTemplateEnum) -> EmailPayload:
    """Cria payload de notificação por email"""
    return EmailPayload(
        user_id=metadata.user_id,
        template=email_template
    )

def compress_images_to_zip(output_directory: str, zip_directory: str, gateway: SliceGatewayInferface,
                            config: VdscConfigDTO) -> None:
    """Compacta imagens do diretório em arquivo ZIP"""
    #Cria lista com nome e dados dos arquivos
    file_info_list = get_file_info_list(output_directory, gateway)

    #Cria buffer zip informando nível de compressão
    buffer_zip = create_zip_buffer(file_info_list, config.vdsc.zip_compression_level)

    #Salva arquivo zip no S3
    gateway.save_file(zip_directory, buffer_zip.read())

def create_interval_list(vdsc_metadata, time_unit_multiplier):
    """Cria lista de intervalos de tempo para extração de frames"""
    start_time = int(vdsc_metadata.start_time * time_unit_multiplier)
    logger.info(f"start_time: {start_time}")
    end_time = int(vdsc_metadata.end_time * time_unit_multiplier)
    logger.info(f"end_time: {end_time}")
    interval = int(vdsc_metadata.time_interval[0]) * int(time_unit_multiplier)
    logger.info(f"interval: {interval}")

    if len(vdsc_metadata.time_interval) == 1:
        time_interval_list = get_recurrent_time_intervals(start_time, end_time, interval)
    else:
        time_interval_list = get_specific_time_intervals(vdsc_metadata.time_interval, int(time_unit_multiplier))
    return time_interval_list

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
        timestamp=datetime.now(),
        is_read=False
    )

def create_zip_buffer(file_info_list: list[tuple[str, bytes]], compression_level: int) -> io.BytesIO:
    """Cria um buffer zip com os arquivos fornecidos"""
    buffer_zip = io.BytesIO()
    with zipfile.ZipFile(buffer_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=compression_level) as zip_file:
        for file_name, file_data in file_info_list:
            zip_file.writestr(file_name, file_data)
    buffer_zip.seek(0)
    return buffer_zip


def encode_frame_to_png(frame, png_compression: int):
    """Codifica frame para formato PNG com nível de compressão especificado"""
    return cv2.imencode('.png', frame, [cv2.IMWRITE_PNG_COMPRESSION, png_compression])


def frame_resize(frame, target_width: int, target_height: int):
    """Redimensiona o frame para as dimensões especificadas"""
    return cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)


def get_file_info_list(output_directory, gateway):
    """Retorna uma lista de tuplas (nome_arquivo, dados_arquivo) do diretório informado"""
    file_list = gateway.get_list_paths_by_directory(output_directory)
    file_info_list = []
    for file_path in file_list:
        file_name = Path(file_path).name
        file_data = gateway.open_file(file_path)
        file_info_list.append((file_name, file_data))
    return file_info_list


def get_frame_size(frame, target_height: int):
    """Obtém o tamanho ajustado do frame mantendo proporção"""
    original_h, original_w = frame.shape[:2]
    if original_h <= target_height:
        return frame
    ratio = target_height / float(original_h)
    target_width = int(original_w * ratio)
    return target_height, target_width


def get_multiplier_time_unit(time_unit: str) -> int:
    """Retorna multiplicador para conversão de unidade de tempo"""
    return 1000 if time_unit == 's' else 1


def get_path_file(prefix_path: str, video_id, extension_file) -> str:
    """Retorna o caminho completo do arquivo"""
    return f"{prefix_path}{video_id}.{extension_file}"


def get_path_directory(prefix_path: str, video_id) -> str:
    """Retorna o caminho completo do diretório"""
    return f"{prefix_path}{video_id}/"


def get_recurrent_time_intervals(start_time: int, end_time: int, interval: int):
    """Gera lista de intervalos de tempo recorrentes"""
    logger.info("Gerando intervalos de tempo recorrentes")
    current_time = start_time
    time_interval_list = []
    while current_time <= end_time:
        time_interval_list.append(current_time)
        current_time += interval
        logger.info(f"time_interval_list: {time_interval_list}")
    return time_interval_list


def get_specific_time_intervals(time_intervals, multiplier: int) -> list[int]:
    """Converte intervalos de tempo específicos para milissegundos"""
    logger.info("Convertendo intervalos de tempo específicos para milissegundos")
    return [int(time) * int(multiplier) for time in time_intervals]


def get_frame_new_size(frame, target_frame_min_size: int) -> tuple[ int, int]:
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
        return int(original_width * ratio),target_frame_min_size
    else:
        # Cenário portrait: a largura é a dimensão limitante, então calcula nova altura mantendo proporção.
        return target_frame_min_size, int(original_height * ratio)


def metadata_update_status(vdsc_metadata: VdscMetadata, new_status: VdscStatusEnum, log: LogEntry) -> VdscMetadata:
    """Atualiza status e adiciona log aos metadados"""
    vdsc_metadata.status = new_status.value
    vdsc_metadata.logs.append(log)
    return vdsc_metadata

def process_video(vdsc_metadata, video_data, video_output_directory, gateway, config: VdscConfigDTO):
    """Processa os frames do vídeo e salva as imagens"""
    #Inicializando variáveis
    resize = False
    new_width = None
    new_height = None
    max_workres = config.vdsc.max_workers

    video_id = vdsc_metadata.video_id
    logger.debug(f"video_id: {video_id}")

    time_unit_multiplier = get_multiplier_time_unit(vdsc_metadata.unit_time)
    logger.debug(f"time_unit_multiplier: {time_unit_multiplier}")

    video_temp_path = create_temporary_file(video_data, vdsc_metadata.extension_file)
    logger.debug(f"video_temp_path: {video_temp_path}")

    output_quality = vdsc_metadata.quality
    logger.debug(f"output_quality: {vdsc_metadata.quality}:{output_quality}")

    png_compression = config.vdsc.png_compression_level
    logger.debug(f"png_compression: {png_compression}")

    process_lock = threading.Lock()
    interval_list = create_interval_list(vdsc_metadata, time_unit_multiplier)

    try:
        vidcap = cv2.VideoCapture(video_temp_path)

        # Validar se precisa de redimensionamento
        if getattr(config.vdsc.quality, output_quality, None) is not None:
            #Obtendo primeiro frame do video para obter dimensões atuais
            vidcap.set(cv2.CAP_PROP_POS_MSEC, 0)
            _, frame = vidcap.read()
            new_width, new_height = get_frame_new_size(frame, getattr(config.vdsc.quality, output_quality, None))
            resize = True

        with ThreadPoolExecutor(max_workers=max_workres) as executor:
            results = executor.map(process_video_frame,
                                   interval_list,
                                   repeat(vidcap),
                                   repeat(resize),
                                   repeat(new_width),
                                   repeat(new_height),
                                   repeat(vdsc_metadata),
                                   repeat(video_output_directory),
                                   repeat(output_quality),
                                   repeat(video_id),
                                   repeat(time_unit_multiplier),
                                   repeat(png_compression),
                                   repeat(gateway),
                                   repeat(process_lock))

        logger.info(f"Processamento realizado com sucesso: {results}")
        vidcap.release()

    except Exception as e:
        logger.error(f"Erro ao processar frames do vídeo ID {video_id}: {str(e)}", exc_info=e)
        raise

def process_video_frame(time_ms: int, vidcap: cv2.VideoCapture, resize: bool, new_width: int, new_height,
                        vdsc_metadata: VdscMetadata, video_output_directory: str, output_quality: str,
                        video_id: str, time_unit_multiplier: int, png_compression: int,
                        gateway: SliceGatewayInferface, process_lock: threading.Lock):
    with process_lock:

        logger.info(f"Capturando frame no tempo(ms): {time_ms}")
        vidcap.set(cv2.CAP_PROP_POS_MSEC, time_ms)
        success, frame = vidcap.read()

    file_output = None

    if success and frame is not None:
        if resize:
            frame = frame_resize(frame, new_width, new_height)

        #Gerando variáveis de output
        suffix_time_file = f"{int(time_ms/time_unit_multiplier)}_{vdsc_metadata.unit_time}"
        logger.info(f"suffix_time_file: {suffix_time_file}")
        file_output = f"{video_output_directory}{video_id}_{output_quality}_{suffix_time_file}.png"
        logger.info(f"file_output: {file_output}")

        #Gerando encode do arquivo
        success, png_data = encode_frame_to_png(frame, png_compression)
        #Salvando arquivo no storage
        gateway.save_file(file_output, png_data.tobytes())
        logger.info(f"Frame salvo com sucesso em: {file_output}")

    else:
        logger.warning(f"Falha ao ler frame no tempo {time_ms}ms")

    return f"Sucesso: {file_output}" if success else f"Erro no tempo {time_ms}"

def set_exception_status(gateway: SliceGatewayInferface, ex: Exception, vdsc_metadata: VdscMetadata, new_status: VdscStatusEnum, config: VdscConfigDTO):
    """Define o status de exceção e retorna metadados e mensagem"""
    match new_status:
        case VdscStatusEnum.FAILED:
            return set_exception_status_failed(gateway, ex, vdsc_metadata)
        case VdscStatusEnum.RETRYING:
            return set_exception_status_retrying(gateway, ex, vdsc_metadata, config)
    return None

def set_exception_status_failed(gateway: SliceGatewayInferface, ex: Exception, vdsc_metadata: VdscMetadata):
    """Define status como FAILED e envia notificação"""
    new_status = VdscStatusEnum.FAILED
    max_retries = vdsc_metadata.max_retry
    video_name = f"{vdsc_metadata.file_name}.{vdsc_metadata.extension_file}"
    message = f" {vdsc_metadata.video_id} - Processamento do video {video_name} falhou após {max_retries} tentativas: {str(ex)}."
    vdsc_metadata = metadata_update_status(vdsc_metadata, new_status, LogEntry(f"Processamento falhou após {max_retries} tentativas."))
    gateway.send_notification(create_notification(vdsc_metadata, ['web','email'], message, EmailTemplateEnum.FAILED))
    return vdsc_metadata, message

def set_exception_status_retrying(gateway: SliceGatewayInferface, ex: Exception, vdsc_metadata: VdscMetadata, config: VdscConfigDTO):
    """Define status como RETRYING e agenda nova tentativa"""
    new_status = VdscStatusEnum.RETRYING
    retries = vdsc_metadata.retries
    max_retries = vdsc_metadata.max_retry
    video_name = f"{vdsc_metadata.file_name}.{vdsc_metadata.extension_file}"
    vdsc_metadata.retries += 1
    message = f"{vdsc_metadata.video_id} - Falha no processamento do video {video_name}: {str(ex)}. Iniciando tentativa {retries+1} de {max_retries}."
    vdsc_metadata = metadata_update_status(vdsc_metadata, new_status, LogEntry(message))
    schedule_timestamp = get_event_schedule_timestamp(vdsc_metadata, retry_backoff_factor = config.vdsc.schedule_event_rules.retry_backoff_factor)
    gateway.send_schedule_retry_event(vdsc_metadata, schedule_timestamp, config.vdsc.schedule_event_rules.to_dict())
    gateway.send_notification(create_notification(vdsc_metadata, ['web','email'], message, EmailTemplateEnum.UPDATE_STATUS))
    return vdsc_metadata, message


