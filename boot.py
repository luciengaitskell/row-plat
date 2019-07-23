from machine import Pin, UART
import uos

u = UART(1, rx=27, tx=33, baudrate=115200)

uos.dupterm(u)
