""" Radio communication layer. """

from comms.packet import Packet

#from devices.rfm69 import RFM69
from settings import VERB

MSG_STORE_SIZE = 255


class Message:
    def __init__(self, mid: int):
        """

        :param mid (int): Global message ID
        :param codec: Encoder/Decoder to utilize for message data
        :param recp (str, default=True): Intended recipient node ID (True for global)
        :param origin (str, default=True): Origin node ID (True for local)
        """
        self._id = mid
        self.packets = []

    def append(self, p: Packet):  # Add another packet of data to message (for sub-packets)
        self.packets.append(p)

    def finalize(self):  # Run decode
        # GET Codec:
        c_id = chr(self.packets[0].codec_id)
        full_body = bytearray()
        for p in self.packets:
            full_body += p.body
        return full_body

    @property
    def max_id(self):
        return self.packets[0].max_id

    @property
    def complete(self):
        return len(self.packets) > self.max_id


class CommsNode:
    def __init__(self, nid: str, radio: "RFM69"):
        """

        :param nid (int): ID of node (any ASCII character)
        :param radio (RFM69): Desired radio to send/recv data
        """
        self.id = ord(nid)
        self._radio = radio

        # Message counters:
        self._curr_msg_id = None  # Next msg_id to use -- int
        self.msg_store = [None for _ in range(MSG_STORE_SIZE)]  # Store of messages -- List[Message]

    @staticmethod
    def _id_difference(p1_id: int, p2_id: int, db: int = 5):
        """
        Difference in packet id from p1 to p2.

        :returns: Split between ids (positive for p2 newer). Will assume shorter route, in case of id wrapping
        """

        diff = p2_id - p1_id
        sign = 1
        if diff < 0:
            sign = -1

        if abs(diff) > MSG_STORE_SIZE / 2:
            diff = abs(diff) - MSG_STORE_SIZE
            diff *= sign

        return diff

    def accept_bytes(self, raw_data: bytes):
        p = Packet.from_raw(raw_data)
        if VERB>2: print("RAW: ", p.to_raw)
        if VERB>2: print("LIST RAW: ", list(p.to_raw))

        if self._curr_msg_id is None:  # New to connection, start at packet
            msg_id = self._curr_msg_id = p.id
            if VERB>0: print("PICKING UP AT ID: ", msg_id)
            if VERB>1: print("RAW: ", list(raw_data))
        else:
            # CHECK Alignment:
            while True:
                diff = self._id_difference(self._curr_msg_id, p.id)
                if diff > 1:  # Much newer packet -> get old ones
                    msg_id = self.next_msg_id
                    self.req_missing(self._curr_msg_id, p.origin_id)
                    #print("from {} to {} of diff {}".format(self._curr_msg_id, p.id, diff))
                elif diff == 1:
                    msg_id = self.next_msg_id
                    break
                else:  # Much older packet -> discard
                    if VERB>0: print("Packet has used ID")
                    return None


        # HANDLE Recp:
        if p.recp_id == chr(0):
            p.recp_id = True

        if p.sub_id == 0:
            msg = Message(msg_id)
            try:  #TODO: TEMPORARY
                self.msg_store[self._curr_msg_id] = msg
            except:
                if VERB>0: print("INDEX: ", self._curr_msg_id)
                raise
        else:
            msg = self.msg_store[self._curr_msg_id]
        msg.append(p)

        if msg.complete:
            # return msg.finalize()  # Return fully combined bodies
            return msg.packets[0]  # For DEBUG: Return first packet -- only 1 packet mode supported
        return False

    def gen_message(self, *args, **kwargs) -> Packet:
        msg_id = self.next_msg_id

        p = Packet(*args, id=msg_id.to_bytes(2, 'little'), origin_id=self.id.to_bytes(1, 'little'), **kwargs)

        if p.sub_id == 0:
            msg = Message(msg_id)
            self.msg_store[self._curr_msg_id] = msg
        else:
            msg = self.msg_store[self._curr_msg_id]
        msg.append(p)
        return p

    @property
    def next_msg_id(self):
        if self._curr_msg_id is None:
            self._curr_msg_id = 0
        else:
            self._curr_msg_id += 1
            if self._curr_msg_id >= MSG_STORE_SIZE:
                self._curr_msg_id = 0
        return self._curr_msg_id

    def req_missing(self, id, recp):
        """ Report to sender (`recp`) that packet of `id` is missing. """
        #print("MISSING ", id)
        return NotImplemented