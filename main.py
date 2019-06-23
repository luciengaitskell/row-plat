"""
Read continually from gps module and save raw return lines to file

Author: Lucien Gaitskell © 2019
"""

from lib.xa1110 import XA1110
from lib import sd
sd.mount()


gps = XA1110()


f = open(sd.ROOT + '/rawnmea.txt', 'a')
try:
    while True:
        for d in gps.read_all_data():
            f.write(d + b'\n')
finally:
    f.close()
    print("SUCCESSFULLY CLOSED FILE")
    sd.unmount()
