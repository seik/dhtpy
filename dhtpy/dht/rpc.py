from __future__ import annotations

import logging
from typing import Callable, Optional, Tuple, Union

from black import os
from dhtpy.bittorrent.bencoding import BencoderError, decode, encode
from dhtpy.config import DEBUG_LEVEL
from dhtpy.dht.structures import Node
from dhtpy.dht.udp import UDPNode

logging.basicConfig(level=DEBUG_LEVEL)
logger = logging.getLogger(__name__)


class RPC:
    def __init__(self):
        self.udp_node = UDPNode()
        self.udp_node.on_data_received = self._on_data_received
        self.udp_node.on_bandwidth_exhausted = self._on_bandwidth_exhausted

        # Callbacks
        self.on_response: Optional[Callable[[dict, Tuple[str, int]], None]] = None
        self.on_bandwidth_exhausted: Optional[Callable[[], None]] = None

    def _on_data_received(self, data: bytes, address: Tuple[str, int]):
        # If port is 0 skip since it cannot be reached
        if address[1] == 0:
            return

        try:
            message = decode(data)
        except BencoderError:
            logging.debug("Error decoding data in RPC._on_data_received")
        else:
            if self.on_response:
                self.on_response(message, address)

    def _on_bandwidth_exhausted(self):
        if self.on_bandwidth_exhausted:
            self.on_bandwidth_exhausted()

    def ping_node(self, nid: int, node: Union[Node, Tuple[str, int]]):
        data = {
            b"y": b"q",
            b"q": b"ping",
            b"t": b"aa",
            b"a": {b"id": nid},
        }
        self.send_message(node, data)

    def find_node(self, nid: int, node: Node):
        data = {
            b"y": b"q",
            b"q": b"find_node",
            b"t": b"aa",
            b"a": {b"id": nid, b"target": node.id},
        }
        self.send_message(node, data)

    def send_message(
        self,
        node: Union[Node, Tuple[str, int]],
        data: dict,
    ):
        address = (node.address, node.port) if isinstance(node, Node) else node
        try:
            message = encode(data)
        except BencoderError:
            logging.debug("Error encoding data in RPC.send_message")
        else:
            self.udp_node.send_message(message, address)

    async def start(self):
        await self.udp_node.start()

    def announce_peer(self, tid: bytes, nid: int, node: Union[Node, Tuple[str, int]]):
        data = {b"t": tid, b"y": b"r", b"r": {b"id": nid}}
        self.send_message(node, data)

    def get_peers(
        self,
        info_hash: bytes,
        node: Node,
        nid: int,
        no_seed=False,
        scrape=False,
    ):
        # TODO transactions id
        data = {
            b"t": os.urandom(2),
            b"y": b"q",
            b"a": {
                b"id": nid,
                b"info_hash": info_hash,
            },
        }

        if no_seed or scrape:
            a = {}
            if no_seed:
                a["noseed"] = 1
            if scrape:
                a["scrape"] = 1
            data[b"a"] = a

        self.send_message(node, data)

    def send_raw_message(self, node: Union[Node, Tuple[str, int]], data: dict):
        self.send_message(node, data)
