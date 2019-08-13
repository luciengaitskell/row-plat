from . import Codec


class TestCodec(Codec):
    @classmethod
    def decode(cls, body: bytes):
        print("Got these: {}".format(body))

    @classmethod
    def encode(cls, data) -> bytes:
        return data.encode('ascii')
