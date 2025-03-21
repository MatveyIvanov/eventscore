from enum import IntEnum


class DeliverySemantic(IntEnum):
    AT_MOST_ONCE = 0
    AT_LEAST_ONCE = 1
    EXACTLY_ONCE = 2


class EventStatus(IntEnum):
    PENDING = 0
    SENT = 1
    FAILED = 2


class PipelineStep(IntEnum):
    NEW = 0
    VALIDATING_ITEMS = 1
    CREATING_WORKERS = 2
    CLONING_WORKERS = 3
