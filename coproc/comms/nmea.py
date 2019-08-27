""" Simple NMEA data transmission. """
from comms.verif import checksum

SENDER_ID = "BX"


class NMEAWriter:
    """ NMEA sentence writer superclass. """
    sentence_id = str

    def __init__(self, data: tuple):
        self.data = data

    def render(self, newline=True):
        if self.sentence_id == NMEAWriter.sentence_id:
            raise ValueError("sentence_id needs definition")

        data_str = ""
        for i, d in enumerate(self.data):
            data_str += str(d)
            if i<len(self.data)-1:
                data_str += ","

        raw = "{}{},{}".format(SENDER_ID, self.sentence_id, data_str)
        raw = raw.encode('ascii')
        csum = checksum(raw)
        raw = b"$" + raw + b"*" + csum
        if newline:
            raw += b'\r\n'
        return raw


class Control(NMEAWriter):
    """ Manual control sentence. """
    sentence_id = "CTL"

    def __init__(self, en, mode, y, r, y_gain, r_gain):
        super().__init__(data=(en, mode, y, r, y_gain, r_gain))
