import serial
import time

from rowplat.motion.platform import Platform
from rowplat.motion.position import Position
from sim.impl.simplethruster import SimpleThruster

DEPLOY = True
if DEPLOY:
    from device.motion.pca9685 import PCA9685
    from device.motion.blue_esc import BlueESC_PCA9685

CTRL_TIMEOUT = 1.000  # (sec) Timeout for thrusters based on last received controller message

if DEPLOY:
    PORT = '/dev/ttyUSB0'  # TODO: REVERT THIS
else:
    PORT = '/dev/tty.usbserial-A4006DBQ'
s = serial.Serial(PORT, 115200)


if DEPLOY:
    pca = PCA9685(0x40)
    pca.set_pwm_freq(300)

    thr = [
        BlueESC_PCA9685(Position(-0.4, -0.25, 0), 3, pca)
        , BlueESC_PCA9685(Position(-0.1, -0.25, 0), 2, pca)
        , BlueESC_PCA9685(Position(0.1, -0.25, 0), 1, pca)
        , BlueESC_PCA9685(Position(0.4, -0.25, 0), 0, pca)
    ]
else:
    thr = [
        SimpleThruster(Position(-0.4, -0.25, 0)),
        SimpleThruster(Position(-0.1, -0.25, 0)),
        SimpleThruster(Position(0.1, -0.25, 0)),
        SimpleThruster(Position(0.4, -0.25, 0))
    ]


plat = Platform(thr)


def interp_joy(v):
    """ Interpret joystick value from encoded transmission """
    v -= 127  # Recenter at 0 (from 127)
    v /= 127  # Scale from +/-127 max
    return v


last_update = None  # Time of last received update from controllers
last_c_mode = 0  # Last controller thruster mode

incoming_buf = b''  # Buffer to store received serial data

while True:
    while s.in_waiting > 0:  # While bytes remain in serial stack
        new = s.read()
        if new == b'\n':  # Marks end of line -> try to decode
            raw = incoming_buf
            incoming_buf = b''
            try:  # Ensure it doesn't crash on error
                # Attempt to select from serial data
                c_enable = raw[0]  # Controller thruster enable state
                c_mode = raw[1]  # Controller thruster mode / layout
                c_y = interp_joy(raw[2])  # Controller y-axis joystick
                c_r = interp_joy(raw[3])  # Controller rotation joystick
                c_g_y = raw[4]  # Controller y-axis gain
                c_g_r = raw[5]  # Controller rotation gain
            except KeyError:
                print("malformed serial data: ", raw)
            else:
                last_update = time.time()  # Set last update timer

                if not c_mode == last_c_mode:  # Handle changing thruster mode
                    plat.disable_thrusters()  # Ensure thrusters are off to prevent one being left on
                    last_c_mode = c_mode
                    if c_mode == 0:
                        plat.thrusters = thr
                    elif c_mode == 1:
                        plat.thrusters = thr[1:3]
                    elif c_mode == 2:
                        plat.thrusters = [thr[0], thr[3]]
                    else:
                        plat.thrusters = []

                if c_enable > 0:
                    plat.set_thrust(0, c_y * c_g_y, c_r * c_g_r)  # Set new thrust
                else:
                    plat.disable_thrusters()
        else:
            incoming_buf += new

    if last_update is None or time.time()-last_update > CTRL_TIMEOUT:
        plat.disable_thrusters()
    print(plat.last_thrust)
    time.sleep(0.1)
