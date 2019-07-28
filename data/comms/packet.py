""" Packet definition for radio communication. """

VERSION = 1


class DataSeg:
    _counter = 0

    def __init__(self, seg_len=1, hidden=False):
        """
        Data segment in a packet, of defined byte length

        :param seg_len (int): Segment length, in bytes.
            * If True, then fill until end of packet.
        """
        self.hidden = hidden
        self.len = seg_len
        self.position = DataSeg._counter

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
    body = DataSeg(seg_len=True)  # Body of message (remaining bytes)

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

    def __init__(self, **kwargs):
        plen = 0
        self.pver = bytes([VERSION])
        for aname, aval in self.seg_iter(False):
            if not aval.hidden:
                plen += len(kwargs[aname])
                setattr(self, aname, kwargs[aname])  # TODO: Need to add check that type is `bytes`, before setting
            else:
                plen += aval.len

        self.plen = bytes([plen])

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
        return cls(**res)

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
            ret[start:end] = seg
        return ret
