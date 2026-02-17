from enum import Enum


class EmailTemplateEnum(str,Enum):
    FAILED = 'FAILED'
    FINISHED = 'FINISHED'
    PROCESSING = 'PROCESSING'
    RETRYING = 'RETRYING'

