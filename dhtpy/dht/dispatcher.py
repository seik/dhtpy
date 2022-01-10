import logging
from abc import abstractmethod
from typing import List, Tuple, cast

from dhtpy.dht import utils as dht_utils
from dhtpy.dht.rpc import RPC
from dhtpy.dht.structures import Node

logger = logging.getLogger(__name__)


# TODO handle sample_infohashes
class DHTDispatcher:
    def __init__(self, rpc: RPC):
        self._running = True

        rpc.on_response = self.on_response
        self._handlers = {
            "get_peers_query": self.on_get_peers_query,
            "get_peers_response": self._get_peers_response,
            "find_node_query": self.on_find_node_query,
            "find_node_response": self._find_node_response,
            "ping_query": self.on_ping_query,
            "ping_response": self._ping_response,
            "announce_peer_response": None,
            "announce_peer_query": self.on_announce_peer_query,
        }

    def _get_node_from_data(self, address: Tuple[str, int], data: dict):
        port = address[1]
        node_id = None

        if b"a" in data:
            node_id = data[b"a"][b"id"]

        if b"r" in data:
            node_id = data[b"r"][b"id"]

        # For queries, if implied_port == 0 then use the port of the data, with the
        # port of the node as fallback in case of a malformed response
        if data.get(b"a") and not data[b"a"].get(b"implied_port", 0):
            port = data[b"a"].get(b"port", address[1])
        return Node(nid=node_id, address=address[0], port=port)

    # Handlers
    # Responses
    def _get_peers_response(self, node: Node, data: dict):
        response = data.get(b"r", {})
        self.on_get_peers_response(
            tid=cast(bytes, data.get(b"t")),
            token=response.get(b"token"),
            nodes=response.get(b"nodes"),
            values=response.get(b"values"),
        )

    def _find_node_response(self, node: Node, data: dict):
        decoded_nodes = dht_utils.decode_nodes(data[b"r"][b"nodes"])
        self.on_find_node_response(cast(bytes, data.get(b"t")), decoded_nodes)

    def _ping_response(self, node: Node, data: dict):
        self.on_ping_node_response(
            tid=cast(bytes, data.get(b"t")),
            node=Node(nid=node.nid, address=node.address, port=node.port),
        )

    def _detect_packet_type_handler(self, data: dict):
        if data.get(b"y") == b"q":
            query = data.get(b"b")
            if query == b"announce_peer":
                method_name = "announce_peer_query"
            elif query == b"find_node":
                method_name = "find_node_query"
            elif query == b"get_peers":
                method_name = "get_peers_query"
            elif query == b"sample_infohashes":
                method_name = "sample_infohashes_query"
            elif query == b"ping":
                method_name = "ping_query"

        if data.get(b"y") == b"r":
            response = data.get(b"r", {})
            if b"values" in response:
                method_name = "get_peers_response"
            elif (
                b"nodes" in response and len(response[b"nodes"]) % 26 == 0
            ):  # Validate nodes format
                method_name = "find_node_response"
            elif set(response.keys()) <= {b"id", b"ip", b"p"}:
                method_name = "ping_response"

        try:
            return self._handlers[method_name]
        except KeyError:
            return None

    # Callbacks

    # Queries
    @abstractmethod
    def on_ping_query(self, node: Node, data: dict):
        pass

    @abstractmethod
    def on_find_node_query(self, node: Node, data: dict):
        pass

    @abstractmethod
    def on_announce_peer_query(self, node: Node, data: dict):
        pass

    @abstractmethod
    def on_get_peers_query(self, node: Node, data: dict):
        pass

    # Responses
    @abstractmethod
    def on_ping_node_response(self, tid: bytes, node: Node):
        pass

    @abstractmethod
    def on_find_node_response(self, tid: bytes, nodes: List[Node]):
        pass

    @abstractmethod
    def on_get_peers_response(
        self,
        tid: bytes,
        token: bytes,
        nodes: List[Node],
        values: List[bytes],
    ) -> None:
        pass

    @abstractmethod
    def on_announce_peer_response(
        self, tid: bytes, nid: bytes, info_hash: bytes, node: Node
    ) -> None:
        pass

    def on_response(self, data: dict, address: Tuple[str, int]) -> None:
        if not self._running:
            return

        packet_type_handler = self._detect_packet_type_handler(data)

        if packet_type_handler:
            node = self._get_node_from_data(address, data)
            packet_type_handler(node=node, data=data)
