from dhtpy.dht.routing import RoutingTable
from dhtpy.dht.structures import Node


class TestRoutingTable:
    def setup_method(self):
        self.routing_table = RoutingTable()

    def test_add_being_empty(self):
        node = Node.create_random("", 1234)
        self.routing_table.add(node)
        assert node in self.routing_table

    def test_split(self):
        assert self.routing_table.split(self.routing_table.buckets[0])
        assert len(self.routing_table.buckets) == 2
