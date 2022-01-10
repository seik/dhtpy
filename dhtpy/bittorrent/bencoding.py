from __future__ import annotations

from io import BytesIO
from typing import Any, Tuple

import better_bencode  # type: ignore


class BencoderError(Exception):
    pass


def encode(obj: Any) -> bytes:
    try:
        return better_bencode.dumps(obj)
    except Exception as e:
        raise BencoderError(e)


def decode(bytes_object: bytes) -> dict:
    try:
        return better_bencode.loads(bytes_object)
    except Exception as e:
        raise BencoderError(e)


def decode2(bytes_object: bytes) -> Tuple[Any, int]:
    bytes_io = BytesIO(bytes_object)
    try:
        return better_bencode.load(bytes_io), bytes_io.tell()
    except Exception as e:
        raise BencoderError(e)
