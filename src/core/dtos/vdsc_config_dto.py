from dataclasses import dataclass

@dataclass(frozen=True)
class QualityDTO:
    ultra: int
    high: int
    medium: int
    low: int

@dataclass(frozen=True)
class ScheduleRulesDTO:
    retry_backoff_factor: int
    retry_arn: str
    retry_role_arn: str
    retry_dlq: str

@dataclass(frozen=True)
class VdscSettingsDTO:
    png_compression_level: int
    zip_compression_level: int
    quality: QualityDTO
    schedule_event_rules: ScheduleRulesDTO

@dataclass(frozen=True)
class S3ConfigDTO:
    bucket_name: str
    dir_uploads: str
    dir_finished: str
    dir_processing: str

@dataclass(frozen=True)
class VdscConfigDTO:
    aws_region: str
    dynamodb_table_name: str
    event_bus_name: str
    s3_bucket: S3ConfigDTO
    vdsc: VdscSettingsDTO

