import logging

from dhtpy.dht.structures import Node

# Crawler
# --------------------------------------------------------
DEBUG_LEVEL = logging.DEBUG
ADDRESS = "0.0.0.0"
PORT = 6881
DHT_BOOTSTRAP_NODES = [
    Node(
        290920051756070156390339148643615988815924871783, "router.bittorrent.com", 6881
    ),
    # TODO: Find real ids
    Node(1, "dht.transmissionbt.com", 6881),
    Node(1, "router.utorrent.com", 6881),
]
METADATA_MAX_SIMULTANEOUS_WORKERS_PER_infohash = 3
METADATA_FETCH_TIMEOUT = 100  # In seconds
