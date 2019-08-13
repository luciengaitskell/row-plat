from data.codec import Codec


THRUST = None  # (int, int)
MODE = None


class ThrusterManual(Codec):
    @classmethod
    def encode(cls, data) -> bytes:
        pass

    @classmethod
    def decode(cls, body: bytes):
        global THRUST
        axis = body[:2], body[2:]

        for i, a in enumerate(axis):
            axis[i] = int.from_bytes(a, 'little')
        THRUST = axis


class ThrusterMode(Codec):
    @classmethod
    def encode(cls, data) -> bytes:
        pass

    @classmethod
    def decode(cls, body: bytes):
        global MODE
        MODE = int.from_bytes(body, 'little')
