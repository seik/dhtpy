from __future__ import annotations

from typing import List, Set

from dhtpy.dht.structures import Bucket, Node, Peer


class SimpleRoutingTable:
    """Naive implementation of the DHT routing table, not efficient but it works
    for simple scenarios."""

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
    """Routing table of the DHT using buckets."""

    def __init__(self):
        self.buckets: List[Bucket] = [
            Bucket(),
        ]

    def __contains__(self, item):
        if isinstance(item, Node):
            for bucket in self.buckets:
                if bucket.in_range(item.id):
                    return item in bucket
        return False

    @property
    def nodes(self) -> Set[Node]:
        # TODO revisit this
        """Returns all nodes of the routing table in a set."""
        nodes = set()
        for bucket in self.buckets:
            for node in bucket.nodes:
                nodes.add(node)
        return nodes

    @property
    def unheard_nodes(self) -> List[Node]:
        """Returns all nodes that are unheard (15 mins no contact) in
        the routing table"""
        return [node for node in self.nodes if node.is_unheard]

    @property
    def offline_nodes(self) -> List[Node]:
        """Returns all nodes that are offline (20 mins no contact) in
        the routing table"""
        return [node for node in self.nodes if node.is_offline]

    def add(self, node: Node) -> bool:
        """Add a node to the routing table, returns if the node has been added.
        If the node belongs to a node that is full this method will attempt to
        split the bucket and add it.
        """
        for bucket in self.buckets:
            if bucket.in_range(node.id):
                added = bucket.add(node)

                if added:
                    return True

                # Node not added, if we can split the bucket, split it and
                # try again to add the node
                if not added and self.split(bucket):
                    return self.add(node)

        return False

    def add_peer(self, peer: Peer, node: Node):
        # TODO: fix
        # self.nodes[node.id].peers[peer.infohash] = peer
        pass

    def get_closest_nodes(self, nid: str, limit=8):
        """Get closest nodes to the id provided"""
        return sorted(
            self.nodes,
            key=lambda node: Node.calculate_distance(nid, node.id),
        )[:limit]

    def get_peers(self, infohash: bytes) -> List[Peer]:
        # TODO: revisit this
        peers = []
        for node in self.nodes:
            if node.peers.get(infohash):
                peers.append(node.peers.get(infohash))
        return peers

    def split(self, bucket: Bucket) -> bool:
        # Maximum number of buckets is 160 per the specification
        if len(self.nodes) == 160:
            return False

        # Cannot split the bucket if there is other bucket bigger than this
        if list(self.buckets).index(bucket) + 1 < len(self.buckets):
            return False

        # Create the new buckets and move nodes between the two
        buckets = [
            Bucket(start=bucket.start, end=bucket.half),
            Bucket(start=bucket.half, end=bucket.end),
        ]
        for new_bucket in buckets:
            for node in bucket.nodes:
                if new_bucket.in_range(node.id):
                    new_bucket.add(node)

        # Replace old bucket and add new one
        old_bucket_index = self.buckets.index(bucket)
        self.buckets[old_bucket_index] = buckets[0]
        self.buckets.append(buckets[1])
        return True
