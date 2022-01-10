from __future__ import annotations

from typing import List, Set

from dhtpy.dht.structures import Node, Peer


class SimpleRoutingTable:
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.nodes: List[Node] = []

    @property
    def is_full(self) -> bool:
        return len(self.nodes) > self.max_size

    @property
    def is_empty(self) -> bool:
        return len(self.nodes) == 0

    def add(self, node: Node) -> bool:
        if not self.is_full:
            self.nodes.append(node)
        return not self.is_full


class RoutingTable(SimpleRoutingTable):
    """More complex routing table, not using buckets as for now"""

    def __init__(self, max_size: int = 10000):
        super().__init__(max_size)
        self.nodes: dict[bytes, Node] = {}  # type: ignore

    @property
    def is_full(self) -> bool:
        return len(self.nodes.values()) > self.max_size

    @property
    def unheard_nodes(self) -> Set[Node]:
        return {node for node in self.nodes.values() if node.is_unheard}

    @property
    def offline_nodes(self) -> Set[Node]:
        return {node for node in self.nodes.values() if node.is_offline}

    def add(self, node: Node):
        if node not in self.nodes.values():
            self.nodes[node.nid] = node
        else:
            # Node is already in the routing table, update last contact
            node.update_last_contact()

    def add_peer(self, peer: Peer, node: Node):
        self.nodes[node.nid].peers[peer.info_hash] = peer

    def get_closest_nodes(self, nid: bytes, limit=10):
        """Get closest nodes to `node`, with a limit of `limit`"""
        return sorted(
            self.nodes.values(),
            key=lambda node: Node.calculate_distance(nid, node.nid),
        )[:limit]

    def get_peers(self, infohash: bytes) -> List[Peer]:
        peers = []
        for node in self.nodes.values():
            if node.peers.get(infohash):
                peers.append(node.peers.get(infohash))
        return peers

    def remove_offline_nodes(self):
        self.nodes = {
            node.nid: node for node in self.nodes.values() if not node.is_offline
        }
