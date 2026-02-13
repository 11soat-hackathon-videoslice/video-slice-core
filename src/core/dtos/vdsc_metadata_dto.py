"""Data Transfer Objects for Video Slice Metadata."""
from dataclasses import dataclass
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from core.domain.vdsc_metadata import VdscMetadata



@dataclass
class LogEntryDTO:
    """DTO for log entry."""

    timestamp: str
    info: str

    def _validate_required_string(self, value: str, field_name: str) -> None:
        """Valida campo string obrigatório"""
        if not value or not isinstance(value, str) or value.strip() == "":
            raise ValueError(f"O campo '{field_name}' é obrigatório e deve ser uma string não vazia")

    def validate(self) -> bool:
        """Valida campos obrigatórios do LogEntry"""
        self._validate_required_string(self.timestamp, "timestamp")
        self._validate_required_string(self.info, "info")
        return True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "info": self.info
        }

@dataclass
class VdscMetadataDTO:
    """DTO for video slice metadata response."""

    video_id: str
    file_name: str
    file_extension: str
    status: str
    created: str
    user_id: str
    total_time: int
    unit_time: str
    start_time: int
    end_time: int
    interval_time: List[str]
    max_retries: int
    retries: int
    resize: str
    quality_output_level: int
    logs: List[LogEntryDTO]

    def _validate_required_string(self, value: str, field_name: str) -> None:
        """Valida campo string obrigatório"""
        if not value or not isinstance(value, str) or value.strip() == "":
            raise ValueError(f"O campo '{field_name}' é obrigatório e deve ser uma string não vazia")

    def _validate_non_negative_integer(self, value: int, field_name: str) -> None:
        """Valida campo inteiro não negativo"""
        if not isinstance(value, int):
            raise ValueError(f"O campo '{field_name}' deve ser um número inteiro")
        if value < 0:
            raise ValueError(f"O campo '{field_name}' deve ser um número positivo ou zero")

    def _validate_string_fields(self) -> None:
        """Valida todos os campos string obrigatórios"""
        self._validate_required_string(self.video_id, "video_id")
        self._validate_required_string(self.file_name, "file_name")
        self._validate_required_string(self.file_extension, "file_extension")
        self._validate_required_string(self.status, "status")
        self._validate_required_string(self.created, "created")
        self._validate_required_string(self.user_id, "user_id")
        self._validate_required_string(self.unit_time, "unit_time")
        self._validate_required_string(self.resize, "resize")

    def _validate_quality_output_level(self) -> None:
        """Valida quality_output_level"""
        if not isinstance(self.quality_output_level, int):
            raise ValueError("O campo 'quality_output_level' deve ser um número inteiro")
        if self.quality_output_level < 1 or self.quality_output_level > 100:
            raise ValueError("O campo 'quality_output_level' deve estar entre 1 e 100")

    def _validate_numeric_fields(self) -> None:
        """Valida todos os campos numéricos"""
        self._validate_non_negative_integer(self.total_time, "total_time")
        self._validate_non_negative_integer(self.start_time, "start_time")
        self._validate_non_negative_integer(self.end_time, "end_time")
        self._validate_non_negative_integer(self.max_retries, "max_retries")
        self._validate_non_negative_integer(self.retries, "retries")

    def _validate_time_range(self) -> None:
        """Valida intervalo de tempo"""
        if self.start_time > self.end_time:
            raise ValueError("O campo 'start_time' não pode ser maior que 'end_time'")

    def _validate_time_interval_list(self) -> None:
        """Valida lista de intervalos de tempo"""
        if not isinstance(self.interval_time, list):
            raise ValueError("O campo 'interval_time' deve ser uma lista")
        if len(self.interval_time) == 0:
            raise ValueError("O campo 'interval_time' não pode ser uma lista vazia")
        for idx, interval in enumerate(self.interval_time):
            if not isinstance(interval, str) or interval.strip() == "":
                raise ValueError(f"O item {idx} do 'interval_time' deve ser uma string não vazia")

    def _validate_logs_list(self) -> None:
        """Valida lista de logs"""
        if not isinstance(self.logs, list):
            raise ValueError("O campo 'logs' deve ser uma lista")
        for idx, log in enumerate(self.logs):
            if not isinstance(log, LogEntryDTO):
                raise ValueError(f"O item {idx} do 'logs' deve ser uma instância de LogEntryDTO")
            try:
                log.validate()
            except Exception as e:
                raise ValueError(f"Erro no log {idx}: {e.args[0] if e.args else str(e)}")

    def validate(self) -> bool:
        """Valida todos os campos do DTO"""
        self._validate_string_fields()
        self._validate_numeric_fields()
        self._validate_quality_output_level()
        self._validate_time_range()
        self._validate_time_interval_list()
        self._validate_logs_list()
        return True

    def to_dict(self) -> dict:
        """Convert DTO to dictionary."""
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
            "logs": [log.to_dict() for log in self.logs]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'VdscMetadataDTO':
        """Create DTO from dictionary."""
        logs_data = data.get('logs', [])
        logs = [
            LogEntryDTO(timestamp=log['timestamp'], info=log['info'])
            if isinstance(log, dict)
            else log
            for log in logs_data
        ]

        return cls(
            video_id=data['videoId'],
            file_name=data['fileName'],
            file_extension=data['fileExtension'],
            status=data['status'],
            created=data['created'],
            user_id=data['userId'],
            total_time=data['totalTime'],
            unit_time=data['unitTime'],
            start_time=data['startTime'],
            end_time=data['endTime'],
            interval_time=data['intervalTime'],
            max_retries=data['maxRetries'],
            retries=data['retries'],
            resize=data['resize'],
            quality_output_level=int(data.get('qualityOutputLevel', 50)),
            logs=logs
        )

    @classmethod
    def from_domain(cls, metadata: 'VdscMetadata') -> 'VdscMetadataDTO':
        """Converte VdscMetadata domain para VdscMetadataDTO"""
        from core.domain.log_entry import LogEntry

        logs_dtos = [
            LogEntryDTO(timestamp=log.timestamp, info=log.info) if isinstance(log, LogEntry)
            else log if isinstance(log, LogEntryDTO)
            else LogEntryDTO(timestamp=log['timestamp'], info=log['info'])
            for log in metadata.logs
        ]

        return cls(
            video_id=metadata.video_id,
            file_name=metadata.file_name,
            file_extension=metadata.file_extension,
            status=metadata.status,
            created=metadata.created,
            user_id=metadata.user_id,
            total_time=metadata.total_time,
            unit_time=metadata.unit_time,
            start_time=metadata.start_time,
            end_time=metadata.end_time,
            interval_time=metadata.interval_time,
            max_retries=metadata.max_retries,
            retries=metadata.retries,
            resize=metadata.resize,
            quality_output_level=metadata.quality_output_level,
            logs=logs_dtos
        )

    @classmethod
    def from_dynamodb_item(cls, item: Dict[str, Any]) -> 'VdscMetadataDTO':
        """Create DTO from DynamoDB item."""
        logs_list = item.get('logs', {}).get('L', [])
        logs = [
            LogEntryDTO(
                timestamp=log_item['M']['timestamp']['S'],
                info=log_item['M']['info']['S']
            )
            for log_item in logs_list
        ]

        return cls(
            video_id=item['videoId']['S'],
            file_name=item['fileName']['S'],
            file_extension=item['fileExtension']['S'],
            status=item['status']['S'],
            created=item['created']['S'],
            user_id=item['userId']['S'],
            total_time=int(item['totalTime']['N']),
            unit_time=item['unitTime']['S'],
            start_time=int(item['startTime']['N']),
            end_time=int(item['endTime']['N']),
            interval_time=[interval['S'] for interval in item['intervalTime']['L']],
            max_retries=int(item['maxRetries']['N']),
            retries=int(item['retries']['N']),
            resize=item['resize']['S'],
            quality_output_level=int(item.get('qualityOutputLevel', {}).get('N', 50)),
            logs=logs
        )

    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Converte DTO para formato DynamoDB"""
        logs_dynamodb = {
            'L': [
                {
                    'M': {
                        'timestamp': {'S': log.timestamp},
                        'info': {'S': log.info}
                    }
                }
                for log in self.logs
            ]
        }

        return {
            'videoId': {'S': str(self.video_id)},
            'fileName': {'S': self.file_name},
            'fileExtension': {'S': self.file_extension},
            'status': {'S': self.status},
            'created': {'S': self.created},
            'userId': {'S': self.user_id},
            'totalTime': {'N': str(self.total_time)},
            'unitTime': {'S': self.unit_time},
            'startTime': {'N': str(self.start_time)},
            'endTime': {'N': str(self.end_time)},
            'intervalTime': {'L': [{'S': interval} for interval in self.interval_time]},
            'maxRetries': {'N': str(self.max_retries)},
            'retries': {'N': str(self.retries)},
            'resize': {'S': self.resize},
            'qualityOutputLevel': {'N': str(self.quality_output_level)},
            'logs': logs_dynamodb
        }


