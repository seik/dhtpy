from __future__ import annotations

import struct
from ctypes import Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from ipaddress import ip_address
from typing import Set

from black import os
from expiringdict import ExpiringDict  # type: ignore


@dataclass
class Node:
    id: str
    address: str
    port: int
    peers = ExpiringDict(max_len=1000, max_age_seconds=3600 * 24)
    added: datetime = datetime.now()
    last_contact: datetime = datetime.now()

    def __hash__(self) -> int:
        return hash(self.id + self.address + str(self.port))

    @property
    def id_bytes(self) -> bytes:
        return bytes.fromhex(self.id)

    @property
    def compact_info(self) -> bytes:
        return struct.pack(
            "!20s4sH",
            self.id_bytes,
            bytes(self.address.encode("ascii")),
            int(self.port),
        )

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

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Node):
            return (
                self.id == other.id
                and self.address == other.address
                and self.port == other.port
            )
        return False

    def __repr__(self) -> str:
        """
        Represents the node in an hex format using the nid.
        """
        return self.id

    @classmethod
    def create_random(cls, address: str, port: int) -> Node:
        """
        Creates a random node with the desired address and port.
        """
        nid = os.urandom(20).hex()
        return cls(nid, address, port)

    @staticmethod
    def calculate_distance(nid: bytes, another_nid: bytes) -> bytes:
        return bytes(a ^ b for a, b in zip(nid, another_nid))

    def update_last_contact(self):
        self.last_contact = datetime.now()


@dataclass
class Peer:
    infohash: bytes
    address: str
    port: int

    @property
    def compact_info(self):
        return struct.pack("!4sH", self.ip.encode("ascii"), self.port)


@dataclass
class Bucket:
    """Representation of a DHT bucket.

    Attributes:
        start (str): represents the hex start of the bucket
        end (str): represents the hex end of the bucket
        capcity (int): capacity of the bucket, this value is also known as K per the
        Kademlia specification
    """

    # TODO keep a cache of good nodes in case a node is removed from a bucket

    start: str = (0).to_bytes(20, "big").hex()
    end: str = ((2 ** 160) - 1).to_bytes(20, "big").hex()  # this equals to ffff...
    capacity: int = 8
    nodes: set[Node] = field(default_factory=set)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Bucket):
            return (
                self.start == other.start
                and self.end == other.end
                and self.capacity == other.capacity
                and self.nodes == other.nodes
            )
        return False

    def __contains__(self, item) -> bool:
        if isinstance(item, Node):
            return item in self.nodes
        return False

    def __hash__(self) -> int:
        return hash((self.start, self.end, self.capacity))

    @property
    def start_bytes(self) -> bytes:
        """Returns start as bytes"""
        return bytes.fromhex(self.start)

    @property
    def end_bytes(self) -> bytes:
        """Returns end as bytes"""
        return bytes.fromhex(self.end)

    @property
    def start_int(self) -> bytes:
        """Returns start as int"""
        return int.from_bytes(self.start_bytes, "big")

    @property
    def end_int(self) -> bytes:
        """Returns end as int"""
        return int.from_bytes(self.end_bytes, "big")

    @property
    def half(self) -> str:
        """Returns the half of the bucket.

        i.e: start=5 end=15 this would return 7"""

        # Shifting a bit results in finding the half between the two numbers
        int_half: int = (self.end_int + self.start_int) >> 1
        return int_half.to_bytes(20, "big").hex()

    def add(self, node: Node) -> bool:
        """Given a node, add it to the bucket"""

        # Node is not in range and max capacity of the bucket reached
        if not self.in_range(node.id) or len(self.nodes) >= self.capacity:
            return False

        # Node already exists in the bucket, update last contact
        if node in self.nodes:
            node.update_last_contact()
            return True

        self.nodes.add(node)
        return True

    def remove(self, node: Node) -> bool:
        """Given a node, remove it from the bucket"""
        self.nodes.remove(node)

    def in_range(self, nid: Union[bytes, int, str]) -> bool:
        """Checks if the node id is in range of this node."""
        if isinstance(nid, str):
            nid = bytes.fromhex(nid)
        return self.start_bytes <= nid < self.end_bytes
