"""
Read continually from gps module and save raw return sentences to a file
Filename includes date and time

Author: Lucien Gaitskell © 2019

190628 RG v2.1 Sync to Github
"""

from lib.xa1110 import XA1110
from lib import sd
import utime
from machine import Pin
# import os

led_red = Pin(13, Pin.OUT)
led_red.off()

print('\nGNSS stored to SD will begin in a few secs (^C to stop) ...')

# Set up communication with GNSS
gps = XA1110()
# Tell GPS to output ZDA time date info every 1 sec (last but one parameter)
gps.write(b'PMTK314,0,1,1,1,1,5,0,0,0,0,0,0,0,0,0,0,0,1,0')
# Clear buffer so that we know that data that followings is current
gps.read_all_data()

#If an additional delay is required to allow ^C before mounting file
utime.sleep_ms(3000) # ms - this is more likely to be compatible than sleep()


# Look for GNZDA sentence that gives the UTC date and time for the filename
date_tag = ''
ii=0
while ii<10 and len(date_tag)==0:
    ii += 1
    # Wait a second, so that ZDA timestamps are present
    utime.sleep_ms(1000)  # ms - this is more likely to be compatible than sleep()
    for d in gps.read_all_data():
        if len(d)>7: # Make sure sentence is reasonable
            # print( d )
            if d[0:7] == b'$GNZDA,':
                # print('***ZDA')
                # Decode the   $GNZDA,hhmmss.ss,dd,mm,yyyy,xx,yy*CC
                date_tag = (d[26:28]+d[21:23]+d[18:20]+'T'+d[7:11]).decode('utf-8') # d[7:11] is hhmm , d[7:13] is hhmmss
                break

if len(date_tag)==0: # We don't have a time so leave it empty
    print( 'WARNING: No ZDA timestamp extracted from GPS after %d attempts'%ii )

# SD Card used to record NMEA o/p from
sd.mount()
print('INFO: SD mounted')

# If we are using default name
filename = sd.ROOT + '/'+date_tag+'_raw_NMEA.txt'
nmea_out_file = open( filename, 'w')
print( 'INFO: Saving to %s'%filename )
led_red.on()

try:
    while True:
        for d in gps.read_all_data():
            nmea_out_file.write( d + b'\n' )
finally:
    led_red.off()
    nmea_out_file.close()
    print("INFO: Closed NMEA Output File - %s"%filename )

    # Not going to unmount so that a following interactive session is possible after ^C the storage
    # sd.unmount()     # Unmount the SD

