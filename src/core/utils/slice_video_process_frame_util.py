import logging
import os
import threading

import cv2
import time

from core.domain.vdsc_metadata import VdscMetadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_video_frame(time_ms: int, video_temp_path: str, resize_params: dict,
                        vdsc_metadata: VdscMetadata, video_output_directory: str, output_quality: str,
                        video_id: str, time_unit_multiplier: int):

    start = time.perf_counter()
    threads_active_count = threading.active_count()
    thread_name = threading.current_thread().name
    logger.debug(f"[PID]: {os.getpid()} | [THREAD]: {thread_name} | [TOTAL THREADS]: {threads_active_count}")
    vidcap = cv2.VideoCapture(video_temp_path)
    file_output = None

    try:
        logger.info(f"Capturando frame no tempo(ms): {time_ms}")
        vidcap.set(cv2.CAP_PROP_POS_MSEC, time_ms)
        success, frame = vidcap.read()

        if success and frame is not None:
            if resize_params['resize']:
                frame = frame_resize(frame, int(resize_params['new_width']), int(resize_params['new_height']))
                logger.debug(f"Frame redimensionado para: {resize_params['new_width']}x{resize_params['new_height']}")

            #Gerando variáveis de output
            suffix_time_file = f"{int(time_ms/time_unit_multiplier)}_{vdsc_metadata.unit_time}"
            logger.debug(f"suffix_time_file: {suffix_time_file}")
            file_output = f"{video_output_directory}{video_id}_{output_quality}_{suffix_time_file}.jpg"
            logger.debug(f"file_output: {file_output}")

            #Gerando encode do arquivo
            success, data = encode_frame_to_jpg(frame, 95)

            end = time.perf_counter()
            logger.debug(f"Tempo de processamento do frame: {end - start:.5f} segundos")##

            return {
                "success": success,
                "file_output": file_output,
                "data": data.tobytes() if success else None,
            }
        else:
            logger.warning(f"Falha ao ler frame no tempo {time_ms}ms")
    finally:
        vidcap.release()

def encode_frame_to_jpg(frame, quality_level: int):
    """Codifica frame para formato PNG com nível de compressão especificado"""
    return cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality_level])

def frame_resize(frame, target_width: int, target_height: int):
    """Redimensiona o frame para as dimensões especificadas"""
    return cv2.resize(frame, (target_width, target_height), interpolation=cv2.INTER_AREA)

def get_frame_size(frame, target_height: int):
    """Obtém o tamanho ajustado do frame mantendo proporção"""
    original_h, original_w = frame.shape[:2]
    if original_h <= target_height:
        return frame
    ratio = target_height / float(original_h)
    target_width = int(original_w * ratio)
    return target_height, target_width