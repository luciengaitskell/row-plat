""" Packet definition for radio communication. """
from data.integrity import verify


VERSION = 1


class DataSeg:
    _counter = 0

    def __init__(self, seg_len=1, raw=False, hidden=False):
        """
        Data segment in a packet, of defined byte length

        :param seg_len (int, default=1): Segment length, in bytes.
            * If True, then fill until end of packet.
        :param raw (bool, default=False): Decides whether to decode from bytes to int
        :param hidden (bool, default=False): Decides whether
        """
        self.hidden = hidden
        self.len = seg_len
        self.position = DataSeg._counter
        self.raw = raw

        if seg_len is True:
            DataSeg._counter = None
        else:
            DataSeg._counter += seg_len

        # TODO: NEED to save default segment types, with conversion to and from bytes


class Packet:
    """ A single packet, for radio communication. """
    plen = DataSeg(hidden=True)  # Packet length
    pver = DataSeg(hidden=True)  # Packet version
    origin_id = DataSeg()  # Packet origin id
    id = DataSeg(2)  # Message id
    recp_id = DataSeg()  # Intended recipient ID
    codec_id = DataSeg()  # Codec ID
    sub_id = DataSeg()  # Message packet sub ID
    max_id = DataSeg()  # Maximum number of packets in message
    csum = DataSeg()  # Checksum
    body = DataSeg(raw=True, seg_len=True)  # Body of message (remaining bytes)

    @classmethod
    def seg_iter(cls, hide=False):
        """
        Iterate through defined packet segments.

        NOTE: Correct order is not guaranteed.
        """
        for aname in dir(cls):
            aval = getattr(cls, aname)
            if isinstance(aval, DataSeg) and not (aval.hidden and hide):
                yield aname, aval

    def __init__(self, *, external=False, **kwargs):
        """ Create Packet object.

        :param external (bool): Enables or disables setting of hidden keys from kwargs.
            * Set to true if data stream is external (and needs checking), or to False if data is internal
        """

        plen = 0
        if not external:
            self.pver = bytes([VERSION])
        for aname, aval in self.seg_iter(False):
            if not aval.hidden or external:
                plen += len(kwargs[aname])
                kwarg_value = kwargs[aname]
                if not aval.raw:
                    kwarg_value = int.from_bytes(kwarg_value, "little")
                setattr(self, aname, kwarg_value)  # TODO: Need to add check that type is `bytes`, before setting
            else:
                plen += aval.len

        if not external:
            self.plen = bytes([plen])
            self.csum = bytes(1)  # TODO: Calculate csum

    @classmethod
    def from_raw(cls, raw_data: bytes):
        """ Create packet object, from raw packet byte string. """
        res = {}
        for aname, aval in cls.seg_iter():
            start = aval.position

            if aval.len is True:
                end = None
            else:
                end = start+aval.len
            res[aname] = raw_data[start: end]
        self = cls(**res)
        self._verify(raw_data)
        return self

    @property
    def to_raw(self):
        """ Create raw packet byte string, from packet object. """
        ret = bytearray(self.plen[0])
        for aname, aval in self.seg_iter():
            seg = getattr(self, aname)
            start = aval.position

            if aval.len is True:
                end = self.plen[0]
            else:
                end = start + aval.len

            if isinstance(seg, int):
                seg = seg.to_bytes(end-start, 'little')
            ret[start:end] = seg
        return ret

    def _verify(self, raw):
        # VERIFY Integrity:
        if not verify(raw, length=self.plen[0], csum=self.csum[0]):
            raise ValueError("Incomprehensible data.")

        # VERIFY Version:
        if VERSION != int.from_bytes(self.pver, 'little'):
            raise ValueError("Mismatched communication version (msg: {}, decoder: {}).".format(self.pver, VERSION))
