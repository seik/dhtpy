import logging

from dhtpy.dht.structures import Node

# Crawler
# --------------------------------------------------------
DEBUG_LEVEL = logging.DEBUG
ADDRESS = "0.0.0.0"
PORT = 6881
DHT_BOOTSTRAP_NODES = [
    Node("32f54e697351ff4aec29cdbaabf2fbe3467cc267", "router.bittorrent.com", 6881),
    # Find real ids
    Node("1", "dht.transmissionbt.com", 6881),
    Node("1", "router.utorrent.com", 6881),
]
METADATA_MAX_SIMULTANEOUS_WORKERS_PER_INFOHASH = 3
METADATA_FETCH_TIMEOUT = 100  # In seconds
