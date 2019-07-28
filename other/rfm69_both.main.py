from devices.rfm69 import RFM69

# Set one of these (for respective radio):
SENDING = False
RECEIVING = False

radio = RFM69(12, 27, baudrate=5000000)
try:
    radio.init(915.0)
    print("temp: ", radio.temperature)
    print("freq: ", radio.frequency_mhz)
    print("powr: ", radio.tx_power)

    if SENDING:
        radio.send(bytes([0x1, 0x2, 0x4, 0xFF]))
        print("SENT")
    if RECEIVING:
        while True:
            print(radio.receive())
finally:
    radio.close()
