import asyncio
import errno
import logging
from asyncio.transports import DatagramTransport
from typing import Callable, Optional, Tuple

from dhtpy.config import ADDRESS, DEBUG_LEVEL, PORT

logging.basicConfig(level=DEBUG_LEVEL)
logger = logging.getLogger(__name__)


class UDPNode(asyncio.DatagramProtocol):
    def __init__(self):
        # Callbacks
        self.on_bandwidth_exhausted: Optional[Callable[[], None]] = None
        self.on_data_received: Optional[Callable[[bytes, Tuple[str, int]], None]] = None

    def connection_made(self, transport: DatagramTransport) -> None:  # type: ignore
        self.transport = transport

    def connection_lost(self, _) -> None:
        self.transport.close()

    def error_received(self, e: Exception) -> None:
        if isinstance(e, PermissionError) or (
            isinstance(e, OSError) and e.errno == errno.ENOBUFS
        ):
            if self.on_bandwidth_exhausted:
                self.on_bandwidth_exhausted()
        else:
            logging.error(f"UDPNode error: {e}")

    def datagram_received(self, data, address: Tuple[str, int]) -> None:
        if self.on_data_received:
            self.on_data_received(data, address)

    async def start(self):
        self.loop = asyncio.get_running_loop()
        await self.loop.create_datagram_endpoint(
            lambda: self, local_addr=(ADDRESS, PORT)
        )

    def send_message(self, data: bytes, address: Tuple[str, int]) -> None:
        self.transport.sendto(data, address)
