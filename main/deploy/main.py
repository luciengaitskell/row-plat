import pynmea2
import serial
import time

from comms import nmea
from rowplat.motion.platform import Platform
from rowplat.motion.position import Position
from sim.impl.simplethruster import SimpleThruster
from store import util as store_util
from store.db import Database


SESSION_NAME = store_util.gen_name()  # Gen session ID/name
print("BEGIN Session ID: {}".format(SESSION_NAME))
DB_PATH = store_util.gen_storage_path(SESSION_NAME)  # Get full path for storage
print("Save data under: {}".format(DB_PATH))
DB = Database(DB_PATH)  # Database accessor object

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


last_update = None  # Time of last received update from controllers
last_c_mode = 0  # Last controller thruster mode

incoming_buf = b''  # Buffer to store received serial data

while True:
    while s.in_waiting > 0:  # While bytes remain in serial stack
        new = s.read()
        if new == b'\n':  # Marks end of line -> try to decode
            incoming_buf += new
            raw = incoming_buf
            incoming_buf = b''

            try:  # Ensure it doesn't crash on error
                nmea_sentence = pynmea2.parse(raw.decode('ascii'))
            except ValueError:
                print("unknown data: ", raw)
            else:
                if isinstance(nmea_sentence, nmea.CTL):
                    # Attempt to select from serial data
                    c_enable = nmea_sentence.enable  # Controller thruster enable state
                    c_mode = nmea_sentence.mode  # Controller thruster mode / layout
                    c_y = nmea_sentence.control_y  # Controller y-axis joystick
                    c_r = nmea_sentence.control_r  # Controller rotation joystick
                    c_g_y = nmea_sentence.gain_y  # Controller y-axis gain
                    c_g_r = nmea_sentence.gain_r  # Controller rotation gain

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

                    if c_enable:
                        plat.set_thrust(0, c_y * c_g_y, c_r * c_g_r)  # Set new thrust
                    else:
                        plat.disable_thrusters()
                elif isinstance(nmea_sentence, nmea.pynmea2.GGA):  # Log fix information
                    ''' NMEA https://www.gpsinformation.org/dale/nmea.htm#GGA '''
                    DB.log({
                        'gps_ts': nmea_sentence.timestamp.strftime("%H%M%S.%f"),
                        'lat': nmea_sentence.latitude,
                        'lon': nmea_sentence.longitude,
                        'fix': nmea_sentence.gps_qual,
                        'sat': nmea_sentence.num_sats,
                    }, mtype='GGA')
                    print("GGA")
                elif isinstance(nmea_sentence, nmea.pynmea2.VTG):  # Log velocity vector information
                    ''' NMEA https://www.gpsinformation.org/dale/nmea.htm#VTG '''
                    DB.log({
                        'true_track': nmea_sentence.true_track,
                        'mag_track': nmea_sentence.mag_track,
                        'spd': nmea_sentence.spd_over_grnd_kmph,
                    }, mtype='VTG')
                    print("VTG")
        else:
            incoming_buf += new

    if last_update is None or time.time()-last_update > CTRL_TIMEOUT:
        plat.disable_thrusters()
    print(plat.last_thrust)
    time.sleep(0.1)
