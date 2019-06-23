from lib.xa1110 import XA1110
from lib.micropygps import MicropyGPS

gps = XA1110()

my_gps = MicropyGPS(location_formatting='dd')



# Reads 300 sentences and reports how many were parsed and if any failed the CRC check
sentence_count = 0


while True:
    line = gps.read_line()

    for c in line:
        stat = my_gps.update(chr(c))
        if stat:
            print(stat)
            stat = None
            sentence_count += 1

    if sentence_count >= 30:
        break


print('Sentences Found:', my_gps.clean_sentences)
print('Sentences Parsed:', my_gps.parsed_sentences)
print('CRC_Fails:', my_gps.crc_fails)

print(my_gps.hdop)
print(my_gps.latitude, my_gps.longitude)
print(my_gps.satellite_data)
