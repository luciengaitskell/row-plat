from data.codec.heartbeat import Heartbeat
from data.codec.thrust import ThrusterManual, ThrusterMode

# Codecs:
from data.codec.test_codec import TestCodec

INCLUDE = [
    TestCodec.setup('a'),
    ThrusterManual.setup('t'),
    ThrusterMode.setup('m'),
    Heartbeat.setup('h')
]  # Codecs to include

LOOKUP = {}  # Dict[str, Codec]
for c in INCLUDE:  # Generate lookup table
    LOOKUP[c.cid] = c
