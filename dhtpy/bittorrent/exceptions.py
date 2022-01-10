from typing import Optional


class MetadataFetcherException(Exception):
    def __init__(self, message: Optional[str]):
        self.message = message


class InvalidHandshake(MetadataFetcherException):
    pass


class InvalidMetadata(MetadataFetcherException):
    pass
