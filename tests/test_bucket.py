from dhtpy.dht.structures import Bucket


class TestBucket:
    def test_half(self):
        bucket = Bucket(start=0, end=4)
        assert bucket.half == 2
