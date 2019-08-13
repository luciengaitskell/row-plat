import time

from data.codec import Codec


class Heartbeat(Codec):
    LAST = None

    @classmethod
    def encode(cls, data) -> bytes:
        pass

    @classmethod
    def decode(cls, body: bytes):
        print("HB")
        cls.LAST = time.ticks_ms()
