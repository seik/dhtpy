from datetime import datetime, timedelta

from dhtpy.dht.structures import Node


class TestNode:
    def test_calculate_distance(self):
        node = Node(b"110", "0.0.0.0", 6881)
        another_node = Node(b"110", "0.0.0.0", 6881)

        # Same nid, no distance
        distance = Node.calculate_distance(node.nid, another_node.nid)
        assert distance == 0

        # Distance should be 1 as only last bit differ
        another_node.nid = b"111"
        distance = Node.calculate_distance(node.nid, another_node.nid)
        assert distance == 1

    def test_is_unheard(self):
        node = Node(b"110", "0.0.0.0", 6881)

        node.last_contact = datetime.now() - timedelta(minutes=10)
        assert not node.is_unheard

        node.last_contact = datetime.now() - timedelta(minutes=15)
        assert node.is_unheard

        node.last_contact = datetime.now() - timedelta(minutes=21)
        assert node.is_unheard

    def test_is_offline(self):
        node = Node(b"110", "0.0.0.0", 6881)

        node.last_contact = datetime.now() - timedelta(minutes=14)
        assert not node.is_offline

        node.last_contact = datetime.now() - timedelta(minutes=15)
        assert not node.is_offline

        node.last_contact = datetime.now() - timedelta(minutes=20)
        assert node.is_offline

    def test_compact_info(self):
        node = Node(b"110", "0.0.0.0", 6881)
        assert (
            node.compact_info
            == b"110\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x000.0.\x1a\xe1"
        )

    def test_hash(self):
        node = Node(b"110", "0.0.0.0", 6881)
        assert hash(node)
