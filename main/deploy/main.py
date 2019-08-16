import serial

from rowplat.motion.platform import Platform
from rowplat.motion.position import Position
from sim.impl.simplethruster import SimpleThruster


s = serial.Serial('/dev/tty.usbserial-A4006DBQ', 115200)

thr = [
    SimpleThruster(Position(-0.1, -0.25, 0)),
    SimpleThruster(Position(-0.4, -0.25, 0)),
    SimpleThruster(Position(0.1, -0.25, 0)),
    SimpleThruster(Position(0.4, -0.25, 0))
]


plat = Platform(thr)

last_update = None
last_mode = 0


def interp_joy(v):
    """ Interpret joystick value from encoded transmission """
    v -= 127  # Recenter at 0 (from 127)
    v /= 127  # Scale from +/-127 max
    return v


while True:
    raw = s.readline()
    raw = raw[:-1]  # Remove last char (newline)

    try:
        data = list(raw)

        # Attempt to pull from serial data
        c_enab = raw[0]
        c_mode = raw[1]
        c_y = interp_joy(raw[2])
        c_r = interp_joy(raw[3])
    except KeyError:
        print("malformed serial data: ", raw)
    else:
        # print(list(raw))
        # print("y: {}; r: {}".format(c_y, c_r))
        if not c_mode == last_mode:
            last_mode = c_mode
            if c_mode == 0:
                plat.thrusters = thr
            elif c_mode == 1:
                plat.thrusters = thr[1:3]
            elif c_mode == 2:
                plat.thrusters = [thr[0], thr[3]]

        plat.set_thrust(0, c_y, c_r)
        print(plat.last_thrust)
