import logging

from dhtpy.dht.structures import Node

# Crawler
# --------------------------------------------------------
DEBUG_LEVEL = logging.DEBUG
ADDRESS = "0.0.0.0"
PORT = 6881
DHT_BOOTSTRAP_NODES = [
    Node(b"32f54e697351ff4aec29cdbaabf2fbe3467cc267", "router.bittorrent.com", 6881),
    # Find real ids
    Node(b"10", "dht.transmissionbt.com", 6881),
    Node(b"11", "router.utorrent.com", 6881),
]
METADATA_MAX_SIMULTANEOUS_WORKERS_PER_INFO_HASH = 3
METADATA_FETCH_TIMEOUT = 100  # In seconds
