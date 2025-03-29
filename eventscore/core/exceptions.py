class EventsCoreError(Exception):
    message = "eventscore error occured."


class AlreadySpawnedError(EventsCoreError):
    message = "Not able to modify consumers after spawning workers."


class ClonesMismatchError(EventsCoreError):
    message = "Pipeline must have the same number of clones for all items."


class EmptyPipelineError(EventsCoreError):
    message = "Pipeline must have at least one item."


class UnrelatedConsumersError(EventsCoreError):
    message = "All consumers in pipeline must be related to the same event."


class EmptyStreamError(EventsCoreError):
    message = "Stream does not have unprocessed messages."


class TooManyDataError(EventsCoreError):
    message = "Unexpected number of data received for event."
