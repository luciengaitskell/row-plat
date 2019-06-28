# 190628 RG v2.1 Sync to Github


from machine import Pin, SDCard
# https://docs.micropython.org/en/latest/library/machine.SDCard.html

import os


ROOT = '/sd'

# Interface config:
COMM_SLOT = 3  # SD Card communication slot number
P_SCK = Pin(5)  # SPI Chip select
P_MISO = Pin(19)  # SPI Master In Slave Out
P_MOSI = Pin(18)  # SPI Master Out Slave In
P_CS = Pin(33)  # SPI Chip Select


def mount():
    """ Setup sd card object and mount to file system. """
    sd = SDCard(slot=COMM_SLOT, sck=P_SCK, miso=P_MISO, mosi=P_MOSI, cs=P_CS)
    os.mount(sd, ROOT)
    return sd


def unmount():
    """ Unmount sd card from file system. """
    os.umount(ROOT)

    """ 
    Sync on all file systems. This would be better than an unmount() since we can continue access interactively. 
    However microPython doesn't have this method 
    """
    # os.sync()


"""
Access the sd card with usual MicroPython file system functions:
 * os.listdir('/sd')
 * open(), write(), close(), etc.
"""
