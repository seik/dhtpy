from dhtpy.dht.routing import RoutingTable
from dhtpy.dht.structures import Node


class TestRoutingTable:
    def setup_method(self):
        self.routing_table = RoutingTable()

    def test_add_being_empty(self):
        node = Node.create_random("", 1234)
        self.routing_table.add(node)
        assert node in self.routing_table

    def test_add_until_split(self):
        for i in range(9):
            nid = i.to_bytes(20, "big").hex()
            node = Node(nid, "", 1234)
            self.routing_table.add(node)

        assert len(self.routing_table.buckets)

    def test_split(self):
        assert self.routing_table.split(self.routing_table.buckets[0])
        assert len(self.routing_table.buckets) == 2

    def test_get_closest_nodes(self):
        nodes = []
        for i in range(9):
            nid = i.to_bytes(20, "big").hex()
            node = Node(nid, "", 1234)
            self.routing_table.add(node)
            nodes.append(node)

        closest_nodes = self.routing_table.get_closest_nodes(
            "0000000000000000000000000000000000000000"
        )
        assert closest_nodes == nodes[:-1]
