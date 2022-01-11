import asyncio
import logging
import os
from typing import List, Tuple, Union

from dhtpy.config import ADDRESS, DHT_BOOTSTRAP_NODES, PORT
from dhtpy.dht.dispatcher import DHTDispatcher
from dhtpy.dht.routing import RoutingTable
from dhtpy.dht.rpc import RPC
from dhtpy.dht.structures import Node, Peer
from dhtpy.dht.utils import join_nodes_compact_info

logger = logging.getLogger(__name__)


class Server(DHTDispatcher):
    def __init__(
        self,
        max_neighbors: int = 10000,
    ):
        """Args:

        max_neighbors: maximum number of neighbors in the crawling service
        """
        self.node = Node.create_random(ADDRESS, PORT)
        # Transaction id used for all queries
        self.tid = os.urandom(2)

        self.rpc: RPC = RPC()

        self.routing_table: RoutingTable = RoutingTable(max_neighbors)
        self._maintain_routing_table_interval = 300  # in seconds

        super().__init__(self.rpc)

    async def _maintain_routing_table(self):
        # Bootstrap
        if self.routing_table.is_empty:
            for node in DHT_BOOTSTRAP_NODES:
                self.routing_table.add(node)
                for _ in range(5):
                    self.find_node(node)

        # Maintain
        self._ping_unheard_nodes()
        self.routing_table.remove_offline_nodes()

    def _ping_unheard_nodes(self):
        for node in self.routing_table.unheard_nodes:
            self.ping_node(node)

    def schedule_maintain_routing_table(self):
        asyncio.ensure_future(self._maintain_routing_table())
        loop = asyncio.get_event_loop()
        loop.call_later(
            self._maintain_routing_table_interval, self.schedule_maintain_routing_table
        )

    # Queries
    def on_ping_query(self, node: Node, data: dict):
        self.send_message(
            node,
            {
                b"t": data[b"t"],
                b"y": b"r",
                b"r": {b"id": self.node.id},
            },
        )

    def on_find_node_query(self, node: Node, data: dict):
        closest_nodes = self.routing_table.get_closest_nodes(data[b"a"][b"target"])
        self.send_message(
            node,
            {
                b"t": data[b"t"],
                b"y": b"r",
                b"r": {
                    b"id": self.node.id,
                    b"nodes": join_nodes_compact_info(closest_nodes),
                },
            },
        )

    def on_announce_peer_query(self, node: Node, data: dict):
        self.routing_table.add_peer(
            Peer(
                info_hash=data[b"a"][b"info_hash"],
                address=node.address,
                port=node.port,
            ),
            node,
        )

        self.send_message(
            node,
            {
                b"t": data[b"t"],
                b"y": b"r",
                b"r": {b"id": node.id},
            },
        )

    def on_get_peers_query(self, node: Node, data: dict):
        peers = self.routing_table.get_peers(data[b"a"][b"info_hash"])
        if peers:
            self.send_message(
                node,
                {
                    b"t": data[b"t"],
                    b"y": b"r",
                    b"r": {
                        b"id": self.node.id,
                        b"token": os.urandom(2),
                        b"values": [peer.compact_info for peer in peers],
                    },
                },
            )
        else:
            closest_nodes = self.routing_table.get_closest_nodes(
                data[b"a"][b"info_hash"]
            )
            self.send_message(
                node,
                {
                    b"t": data[b"t"],
                    b"y": b"r",
                    b"r": {
                        b"id": self.node.id,
                        b"nodes": join_nodes_compact_info(closest_nodes),
                    },
                },
            )

    # Responses
    def on_ping_response(self, tid: bytes, node: Node):
        # TODO fix, not needed
        return super().on_ping_response(tid, node)

    def on_find_node_response(self, tid: bytes, nodes: List[Node]):
        """Found a node, if the table is not full and the node is valid, add it"""
        nodes = [node for node in nodes if self.node != node and node.is_valid]
        for node in nodes:
            self.routing_table.add(node)

    def on_announce_peer_response(
        self, tid: bytes, nid: int, info_hash: bytes, node: Node
    ):
        logger.debug(f"On announce peer, infohash {info_hash.hex()}")

    def on_get_peers_response(
        self, tid: bytes, token: bytes, node: List[Node], values: List[bytes]
    ):
        logger.debug(f"On get peers")

    # Messages
    def ping_node(self, node: Union[Node, Tuple[str, int]]):
        self.rpc.ping_node(self.node.id, node)

    def find_node(self, node: Node):
        self.rpc.find_node(self.node.id, node)

    def announce_peer(self, node: Union[Node, Tuple[str, int]]):
        self.rpc.announce_peer(self.tid, self.node.id, node)

    def get_peers(
        self,
        info_hash: bytes,
        no_seed: bool = False,
        scrape: bool = False,
    ) -> None:
        # TODO: fix None, should be a node to contact, using closest in routing table
        self.rpc.get_peers(self.tid, info_hash, None, self.node.id, no_seed, scrape)  # type: ignore

    async def start(self, address: str = "0.0.0.0", port: int = 6881, run_forever=True):
        await self.rpc.start()
        self.schedule_maintain_routing_table()

        if run_forever:
            loop = asyncio.get_running_loop()
            loop.run_forever()

    async def stop(self):
        pass

    def send_message(
        self,
        node: Union[Node, Tuple[str, int]],
        data: dict,
    ):
        self.rpc.send_raw_message(node, data)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    server = Server()
    loop.run_until_complete(server.start(run_forever=False))
    loop.run_forever()
