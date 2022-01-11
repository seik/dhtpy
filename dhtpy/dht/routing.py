from __future__ import annotations

from typing import List, Set

from dhtpy.dht.structures import Bucket, Node, Peer


class SimpleRoutingTable:
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.nodes: List[Node] = list()

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


class RoutingTable:
    """More complex routing table, not using buckets as for now"""

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.buckets: Set[Bucket] = {
            Bucket(0, 2 ** 160),
        }

    @property
    def nodes(self) -> List[Node]:
        return []

    @property
    def unheard_nodes(self) -> List[Node]:
        return [node for node in self.nodes if node.is_unheard]

    @property
    def offline_nodes(self) -> List[Node]:
        return [node for node in self.nodes if node.is_offline]

    def _split(self, bucket: Bucket) -> bool:
        pass

    def add(self, node: Node) -> bool:
        # TODO: fix
        for bucket in self.buckets:
            if bucket.in_range(node.id):
                pass

        return False
        # Node is already in the routing table, update last contact
        node.update_last_contact()

    def add_peer(self, peer: Peer, node: Node):
        # TODO: fix
        self.nodes[node.id].peers[peer.info_hash] = peer

    def get_closest_nodes(self, nid: int, limit=10):
        """Get closest nodes to `node`, with a limit of `limit`"""
        return sorted(
            self.nodes,
            key=lambda node: Node.calculate_distance(nid, node.id),
        )[:limit]

    def get_peers(self, infohash: bytes) -> List[Peer]:
        peers = []
        for node in self.nodes:
            if node.peers.get(infohash):
                peers.append(node.peers.get(infohash))
        return peers

    def remove_offline_nodes(self):
        self.nodes = {
            node.id: node for node in self.nodes.values() if not node.is_offline
        }
