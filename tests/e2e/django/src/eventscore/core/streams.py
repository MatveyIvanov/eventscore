from typing import Any

from eventscore.core.abstract import IStream, IStreamFactory


class StreamFactory(IStreamFactory):
    def __init__(self, stream_class: type[IStream], kwargs: dict[str, Any]) -> None:
        self.__stream_class = stream_class
        self.__kwargs = kwargs

    def __call__(self) -> IStream:
        return self.__stream_class(**self.__kwargs)
