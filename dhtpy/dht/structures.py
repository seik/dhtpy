from __future__ import annotations

import os
import struct
from dataclasses import dataclass
from datetime import datetime, timedelta
from ipaddress import ip_address

from expiringdict import ExpiringDict  # type: ignore


@dataclass
class Node:
    nid: bytes
    address: str
    port: int
    peers = ExpiringDict(max_len=1000, max_age_seconds=3600 * 24)
    added: datetime = datetime.now()
    last_contact: datetime = datetime.now()

    @property
    def compact_info(self):
        return struct.pack(
            "!20s4sH",
            self.nid,
            bytes(self.address.encode("ascii")),
            int(self.port),
        )

    @property
    def hex_id(self) -> str:
        return self.nid.hex()

    @property
    def is_address_public(self) -> bool:
        return not ip_address(self.address).is_private

    @property
    def is_valid(self) -> bool:
        return self.is_address_public and self.is_valid_port

    @property
    def is_valid_port(self) -> bool:
        return 0 < self.port < 65536

    @property
    def is_unheard(self) -> bool:
        return datetime.now() > (self.last_contact + timedelta(minutes=15))

    @property
    def is_offline(self) -> bool:
        return datetime.now() > (self.last_contact + timedelta(minutes=20))

    def __hash__(self) -> int:
        return hash(self.nid.hex() + self.address + str(self.port))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Node):
            return (
                self.nid == other.nid
                and self.address == other.address
                and self.port == other.port
            )
        return False

    def __repr__(self) -> str:
        """
        Represents the node in an hex format using the nid.
        """
        return self.hex_id

    @classmethod
    def create_random(cls, address: str, port: int) -> Node:
        """
        Creates a random node with the desired address and port.
        """
        nid = Node.generate_random_id()
        return cls(nid, address, port)

    @staticmethod
    def generate_random_id() -> bytes:
        """
        Generates a random node id which consists of 20 bytes.
        """
        return os.urandom(20)

    @staticmethod
    def calculate_distance(nid: bytes, another_nid: bytes) -> int:
        bytes_distance = bytes(a ^ b for a, b in zip(nid, another_nid))
        return int.from_bytes(bytes_distance, byteorder="big")

    def update_last_contact(self):
        self.last_contact = datetime.now()


@dataclass
class Peer:
    info_hash: bytes
    address: str
    port: int

    @property
    def compact_info(self):
        return struct.pack("!4sH", self.ip.encode("ascii"), self.port)
