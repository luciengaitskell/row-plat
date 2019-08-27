def checksum(raw, hex_str=True):
    """
    Generate checksum for comms string.

    :param raw: str
        Input command string
    :param hex_str: str (default=True)
        Enable return as byte string of checksum in hexadecimal, without the leading '0x'
    """
    t = 0

    for i in range(0, len(raw)):
        t = t ^ raw[i]

    # "{0:#0{1}x}".format(42,6) - see https://stackoverflow.com/questions/12638408/decorating-hex-function-to-pad-zeros

    if hex_str:
        # return hex(t).strip('0x').upper().encode('ascii') # This argument provides no leading 0, so not suitable
        return "{:0>2X}".format(t).encode('ascii') # Ensures leading 0 in hex, two characters

    return t
