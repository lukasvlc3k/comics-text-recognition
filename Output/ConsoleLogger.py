import string
from enum import Enum


class Verbosity(Enum):
    NONE = 0
    WARNING = 1
    INFO = 2
    DEBUG = 3


class EventType(Enum):
    WARNING = 1
    INFO = 2
    DEBUG = 3


class ConsoleLogger:
    def __init__(self, verbose_level: Verbosity):
        self.verbose_level = verbose_level

    def log(self, log_type: EventType, text: string):
        if log_type.value <= self.verbose_level.value:
            print(text)

    def info(self, text):
        return self.log(EventType.INFO, text)

    def warning(self, text):
        return self.log(EventType.WARNING, text)

    def debug(self, text):
        return self.log(EventType.DEBUG, text)
