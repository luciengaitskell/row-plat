from abc import abstractmethod


class Codec:
    """
    Handles encoding and decoding of comms data.

    Additionally will store last values of respective messages.
    """
    cid = None

    @classmethod
    def setup(cls, cid):
        cls.cid = cid
        return cls

    @classmethod
    @abstractmethod
    def encode(cls, data) -> bytes:
        pass

    @classmethod
    @abstractmethod
    def decode(cls, body: bytes):
        pass
