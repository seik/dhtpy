from datetime import datetime, timedelta

from dhtpy.dht.structures import Bucket, Node


class TestNode:
    def setup_method(self, test_method):
        self.node = Node("0000000000000000000000000000000000000001", "0.0.0.0", 1234)

    def test_create_random(self):
        node = Node.create_random("", 1234)
        assert isinstance(node.id, str)
        assert isinstance(node.address, str)
        assert isinstance(node.port, int)

    def test_calculate_distance(self):
        another_node = Node.create_random("0.0.0.0", 1234)
        # same id, no distance
        another_node.id = self.node.id
        distance = Node.calculate_distance(self.node.id, another_node.id)
        assert distance == 0

        # distance should be 1 as only last bit differ
        self.node.id = "0000000000000000000000000000000000000010"
        another_node.id = "0000000000000000000000000000000000000011"
        distance = Node.calculate_distance(self.node.id, another_node.id)
        assert distance == 1

    def test_is_unheard(self):
        self.node.last_contact = datetime.now() - timedelta(minutes=10)
        assert not self.node.is_unheard

        self.node.last_contact = datetime.now() - timedelta(minutes=15)
        assert self.node.is_unheard

        self.node.last_contact = datetime.now() - timedelta(minutes=21)
        assert self.node.is_unheard

    def test_is_offline(self):
        self.node.last_contact = datetime.now() - timedelta(minutes=14)
        assert not self.node.is_offline

        self.node.last_contact = datetime.now() - timedelta(minutes=15)
        assert not self.node.is_offline

        self.node.last_contact = datetime.now() - timedelta(minutes=20)
        assert self.node.is_offline

    def test_compact_info(self):
        self.node.id = "0000000000000000000000000000000000000001"
        assert (
            self.node.compact_info
            == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x010.0.\x04\xd2"
        )

    def test_hash(self):
        assert hash(self.node)


class TestBucket:
    def test_half(self):
        bucket = Bucket(
            start="0000000000000000000000000000000000000000",
            end="0000000000000000000000000000000000000004",
        )
        assert bucket.half == "0000000000000000000000000000000000000002"

    def test_in(self):
        bucket = Bucket()

        node = Node.create_random("", 1234)
        another_node = Node.create_random("", 1234)

        bucket.add(node)
        bucket.add(another_node)

        assert node in bucket
