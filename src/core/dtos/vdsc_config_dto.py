from dataclasses import dataclass

@dataclass(frozen=True)
class ResizeDTO:
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
    def to_dict(self):
        return {
            'retry_backoff_factor': self.retry_backoff_factor,
            'retry_arn': self.retry_arn,
            'retry_role_arn': self.retry_role_arn,
            'retry_dlq': self.retry_dlq
        }

@dataclass(frozen=True)
class VdscSettingsDTO:
    dir_uploads: str
    dir_finished: str
    dir_tmp: str
    max_workers: int
    resize: ResizeDTO
    schedule_event_rules: ScheduleRulesDTO

@dataclass(frozen=True)
class VdscConfigDTO:
    aws_region: str
    s3_bucket_name: str
    dynamodb_table_name: str
    event_bus_name: str
    vdsc: VdscSettingsDTO
