from machine import Pin, UART
import uos


u = UART(1, rx=33, tx=15, baudrate=115200)

uos.dupterm(u)
