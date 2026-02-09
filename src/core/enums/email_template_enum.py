from enum import Enum, auto


class EmailTemplateEnum(str,Enum):
    UPDATE_STATUS = auto()
    FAILED = auto()
    FINISHED = auto()
