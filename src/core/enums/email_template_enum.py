from enum import Enum, auto


class EmailTemplateEnum(Enum):
    UPDATE_STATUS = auto()
    FAILED = auto()
    FINISHED = auto()
