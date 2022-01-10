from dhtpy.dht.routing import RoutingTable
from dhtpy.dht.structures import Node


class TestRoutingTable:
    def test_get_closest_nodes(self):
        routing_table = RoutingTable()

        local_node = Node(b"1100", "0.0.0.0", 6881)
        closest_node = Node(b"1110", "0.0.0.0", 6881)
        farthest_node = Node(b"1111", "0.0.0.0", 6881)

        routing_table.add(farthest_node)
        routing_table.add(closest_node)

        assert routing_table.get_closest_nodes(local_node.nid) == [
            closest_node,
            farthest_node,
        ]
