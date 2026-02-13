"""Video Slice Metadata domain entity."""
from datetime import datetime
from typing import List, Optional

from .log_entry import LogEntry
from ..dtos.vdsc_metadata_dto import VdscMetadataDTO
from ..enums.vdsc_status_enum import VdscStatusEnum
from ..enums.video_resize_enum import VideoResize


class VdscMetadata:
    def __init__(
        self,
        dto: VdscMetadataDTO,
        logs: Optional[List[LogEntry]] = None
    ):
        self.video_id = dto.video_id
        self.file_name = dto.file_name
        self.file_extension = dto.file_extension
        self.status = dto.status
        # Campo created é string no formato ISO 8601
        self.created = dto.created
        self.user_id = dto.user_id
        self.total_time = dto.total_time
        self.unit_time = dto.unit_time
        self.start_time = dto.start_time
        self.end_time = dto.end_time
        self.interval_time = dto.interval_time if dto.interval_time else []
        self.max_retries = dto.max_retries
        self.retries = dto.retries
        self.resize = dto.resize
        self.quality_output_level = dto.quality_output_level
        self.logs = dto.logs if dto.logs else []

    def validate(self) -> bool:
        """Valida as regras de negócio para metadados de slice de vídeo."""
        self._validate_required_fields()
        self._validate_time_fields()
        self._validate_retry_fields()
        self._validate_enums()
        self._validate_quality_output_level()
        return True

    def _validate_required_fields(self) -> None:
        """Valida campos obrigatórios."""
        if not self.video_id or not self.user_id:
            raise ValueError("ID do vídeo e ID do usuário são obrigatórios")
        if not self.file_name:
            raise ValueError("Nome do arquivo é obrigatório")
        if not self.file_extension:
            raise ValueError("Extensão do arquivo é obrigatória")

    def _validate_time_fields(self) -> None:
        """Valida campos relacionados a tempo."""
        if self.total_time <= 0:
            raise ValueError("Tempo total deve ser maior que zero")
        if self.start_time < 0:
            raise ValueError("Tempo inicial não pode ser negativo")
        if self.end_time <= self.start_time:
            raise ValueError("Tempo final deve ser maior que o tempo inicial")
        if self.end_time > self.total_time:
            raise ValueError("Tempo final não pode exceder o tempo total")
        if self.unit_time not in ["s", "ms", "m", "h"]:
            raise ValueError("Unidade de tempo deve ser uma das seguintes: s, ms, m, h")

    def _validate_retry_fields(self) -> None:
        """Valida campos de retentativa."""
        if self.max_retries < 0:
            raise ValueError("Número máximo de tentativas não pode ser negativo")
        if self.retries < 0:
            raise ValueError("Número de tentativas não pode ser negativo")
        if self.retries > self.max_retries:
            raise ValueError("Número de tentativas não pode exceder o máximo permitido")

    def _validate_enums(self) -> None:
        """Valida valores de enumerações."""
        if not VideoResize.is_valid(self.resize):
            valid_qualities = VideoResize.get_all_values()
            raise ValueError(f"Qualidade deve ser uma das seguintes: {', '.join(valid_qualities)}")
        if not VdscStatusEnum.is_valid(self.status):
            valid_statuses = VdscStatusEnum.get_all_values()
            raise ValueError(f"Status deve ser um dos seguintes: {', '.join(valid_statuses)}")

    def _validate_quality_output_level(self) -> None:
        """Valida o nível de qualidade de saída."""
        if not isinstance(self.quality_output_level, int):
            raise ValueError("O campo 'quality_output_level' deve ser um número inteiro")
        if self.quality_output_level < 1 or self.quality_output_level > 100:
            raise ValueError("O campo 'quality_output_level' deve estar entre 1 e 100")


    def add_log(self, info: str, timestamp: Optional[datetime] = None):
        """Adiciona uma entrada de log aos metadados."""
        log_entry = LogEntry(info=info, timestamp=timestamp)
        self.logs.append(log_entry)

    def _update_status(self, new_status: str, log_info: str):
        """Atualiza o status dos metadados e adiciona uma entrada de log."""
        self.status = new_status
        self.add_log(log_info)

    def mark_as_uploaded(self):
        """Marca os metadados como enviado."""
        self._update_status(VdscStatusEnum.UPLOADED.value, "uploaded")

    def mark_as_processing(self):
        """Marca os metadados como em processamento."""
        self._update_status(VdscStatusEnum.PROCESSING.value, "processing")

    def mark_as_finished(self):
        """Marca os metadados como finalizado."""
        self._update_status(VdscStatusEnum.FINISHED.value, "finished")

    def mark_as_retrying(self):
        """Marca os metadados como retentativa."""
        self._update_status(VdscStatusEnum.RETRYING.value, "retrying")

    def mark_as_failed(self, error_message: Optional[str] = None):
        """Marca os metadados como falhou."""
        self._update_status(VdscStatusEnum.FAILED.value, f"failed: {error_message}" if error_message else "failed")

    def increment_retry(self) -> bool:
        """Incrementa o contador de tentativas. Retorna True se ainda é possível tentar novamente, False se o máximo foi atingido."""
        if self.retries >= self.max_retries:
            return False
        self.retries += 1
        self.add_log(f"tentativa {self.retries} de {self.max_retries}")
        return True

    def can_retry(self) -> bool:
        """Verifica se ainda é possível realizar nova tentativa."""
        return self.retries < self.max_retries

    def get_duration(self) -> int:
        """Obtém a duração do slice na unidade especificada."""
        return self.end_time - self.start_time

    def get_full_file_name(self) -> str:
        """Obtém o nome completo do arquivo com extensão."""
        return f"{self.file_name}.{self.file_extension}"

    def to_dict(self) -> dict:
        """Converte os metadados para representação em dicionário."""
        return {
            "videoId": self.video_id,
            "fileName": self.file_name,
            "fileExtension": self.file_extension,
            "status": self.status,
            "created": self.created,
            "userId": self.user_id,
            "totalTime": self.total_time,
            "unitTime": self.unit_time,
            "startTime": self.start_time,
            "endTime": self.end_time,
            "intervalTime": self.interval_time,
            "maxRetries": self.max_retries,
            "retries": self.retries,
            "resize": self.resize,
            "qualityOutputLevel": self.quality_output_level,
            "logs": [log.to_dict() if isinstance(log, LogEntry) else log for log in self.logs]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'VdscMetadata':
        """Cria VideoSliceMetadata a partir de um dicionário."""
        logs_data = data.get('logs', [])
        logs = [LogEntry.from_dict(log) if isinstance(log, dict) else log for log in logs_data]

        dto = VdscMetadataDTO(
            video_id=data['videoId'],
            file_name=data['fileName'],
            file_extension=data.get('fileExtension', data.get('extensionFile', 'mp4')),
            status=data.get('status', VdscStatusEnum.UPLOADED.value),
            created=data.get('created'),
            user_id=data['userId'],
            total_time=data['totalTime'],
            unit_time=data.get('unitTime', 's'),
            start_time=data['startTime'],
            end_time=data['endTime'],
            interval_time=data.get('intervalTime', data.get('timeInterval', [])),
            max_retries=data.get('maxRetries', data.get('maxRetry', 3)),
            retries=data.get('retries', 0),
            resize=data.get('resize', VideoResize.HIGH.value),
            quality_output_level=data.get('qualityOutputLevel', 'high'),
            logs=logs
        )

        return cls(dto=dto)

    def __repr__(self) -> str:
        return (f"VideoSliceMetadata(video_id='{self.video_id}', "
                f"file_name='{self.file_name}', status='{self.status}', "
                f"user_id='{self.user_id}', retries={self.retries}/{self.max_retries})")


