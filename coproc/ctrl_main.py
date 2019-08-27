import time
import math
from framebuf import FrameBuffer, MONO_VLSB

from machine import I2C, Pin

from platform import Platform, SSD1306_I2C
from ui.button import Button


LOOP_PERIOD = 50
TX_PERIOD = 500

plat = Platform('r', display=False)

# Display:
_oled_rst = Pin(33, mode=Pin.OUT)  # Define OLED reset pin
#   Run reset procedure to allow for communication:
_oled_rst.value(0)
time.sleep_ms(20)
_oled_rst.value(1)
time.sleep_ms(20)
#   Initialize display:
plat.display = SSD1306_I2C(128, 64, plat.i2c_bus, 0x3D)


# Buttons -- NOTE: Pull Ups do not seem to work on these pins: 36, 39, 34; used external pull-up
#            NOTE 2: Values are INVERTED (0/low -> on; 1/high -> off)
B_UP = Button(Pin(36, Pin.IN, Pin.PULL_UP))
B_DOWN = Button(Pin(4, Pin.IN, Pin.PULL_UP))
B_LEFT = Button(Pin(39, Pin.IN, Pin.PULL_UP))
B_RIGHT = Button(Pin(34, Pin.IN, Pin.PULL_UP))

B_ENB = Pin(14, Pin.IN, Pin.PULL_UP)
B_ALT = Button(Pin(32, Pin.IN, Pin.PULL_UP))


# Shared variables:

last_success = None


class Control:
    """ Control variables used to send to boat. """
    enable = False  # (bool) General lockout for motors
    mode = 0  # (int) Drive mode/motor layout -- 0: all, 1: inner, 2: outer, 3: gain edit
    y = 0  # (float) Y-axis control (throttle)
    r = 0  # (float) Rotational axis control
    g_y = 1  # (int) Y-axis gain
    g_r = 1  # (int) Rotational axis gain

    @staticmethod
    def _scale_joy(v):
        if abs(v) < 0.01:  # Prevent small values from scaling up
            v = 0
        v *= 127.  # Make [-127, 127]
        v += 127   # Make [0, 254] (center of 127)
        return int(v)

    @classmethod
    def gen_control_string(cls):
        enable = int(cls.enable)
        mode = cls.mode

        y = cls._scale_joy(cls.y)
        r = cls._scale_joy(cls.r)

        g_y = int(cls.g_y)
        g_r = int(cls.g_r)

        return bytes([enable, mode, y, r, g_y, g_r])


# # INTERACTION
def button_detect():
    # Throttle control
    y_delta = 0  # Button change to y-axis control value
    if B_UP.update() and not B_UP.last:
        y_delta += 1
    if B_DOWN.update() and not B_DOWN.last:
        y_delta -= 1

    # Rotation control
    r_delta = 0  # Button change to rotational control value
    if B_RIGHT.update() and not B_RIGHT.last:
        r_delta += 1
    if B_LEFT.update() and not B_LEFT.last:
        r_delta -= 1

    if Control.mode == 3:  # Detect for gain edit mode
        # Ensure control at center:
        Control.y = 0
        Control.r = 0

        Control.g_y += y_delta
        Control.g_r += r_delta
    else:
        Control.y += y_delta * 0.1
        Control.r += r_delta * 0.1

    # Control clamping:
    if abs(Control.y) > 1.0:  # Clamp to [-1.0, 1.0]
        Control.y = math.copysign(1.0, Control.y)
    if abs(Control.r) > 1.0:  # Clamp to [-1.0, 1.0]
        Control.r = math.copysign(1.0, Control.r)

    # Control gain clamping:
    if Control.g_y < 1:
        Control.g_y = 1
    if Control.g_y > 9:
        Control.g_y = 9
    if Control.g_r < 1:
        Control.g_r = 1
    if Control.g_r > 9:
        Control.g_r = 9

    Control.enable = not B_ENB.value()  # Enable switch (latching)

    # Mode switch:
    if B_ALT.update() and not B_ALT.last:
        Control.mode += 1
        if Control.mode > 3:
            Control.mode = 0


# # DISPLAY
CROSS_BORDER = 5
CROSS_LEN = 65-(CROSS_BORDER*2)
CROSS_CENTER = (32, 32)   # Control cross config
CROSS_ICN_WIDTH = 3
M_START = 64+5
M_SIZE = 10
M_BUF = 2

# BUILD template:
screen_template = FrameBuffer(bytearray(len(plat.display.buffer)), plat.display.width, plat.display.height, MONO_VLSB)

#  control cross
screen_template.vline(CROSS_CENTER[0], CROSS_BORDER, CROSS_LEN, 1)
screen_template.hline(CROSS_BORDER, CROSS_CENTER[1], CROSS_LEN, 1)

#  motors:
screen_template.text("43 21", M_START+3, int(32-M_SIZE/2) - 8)
M_DATA = [  # x, y, h, w, c  == for each motor display box
    (M_START, int(32-M_SIZE/2), M_SIZE, M_SIZE, 1),  # motor 4 indicator (left)
    (M_START + M_SIZE + M_BUF, int(32-M_SIZE/2), M_SIZE, M_SIZE, 1),  # motor 3 indicator
    (M_START + (M_SIZE + M_BUF)*2, int(32-M_SIZE/2), M_SIZE, M_SIZE, 1),  # motor 2 indicator
    (M_START + (M_SIZE + M_BUF)*3, int(32-M_SIZE/2), M_SIZE, M_SIZE, 1)  # motor 1 indicator (right)
]

for m_args in M_DATA:
    screen_template.rect(*m_args)


def update_display():
    plat.display.fill(0)  # Clear screen

    # Apply template:
    plat.display.blit(screen_template, 0, 0)

    # Thrusters enabled display:
    if Control.enable:
        _active = "RUN"
    else:
        _active = "OFF"
    plat.display.text(_active, 105, 56)

    # Motor active display
    if Control.mode == 0 or Control.mode == 1:  # inner (m3 and m2)
        plat.display.fill_rect(*M_DATA[1])
        plat.display.fill_rect(*M_DATA[2])
    if Control.mode == 0 or Control.mode == 2:  # inner (m4 and m1)
        plat.display.fill_rect(*M_DATA[0])
        plat.display.fill_rect(*M_DATA[3])
    if Control.mode == 3:
        plat.display.text("GAIN", 64, 56)

    # Cross point placement
    plat.display.rect(
        int(Control.r * (CROSS_LEN-1) / 2 + CROSS_CENTER[0] - CROSS_ICN_WIDTH / 2)+1,
        int(-Control.y * (CROSS_LEN-1) / 2 + CROSS_CENTER[1] - CROSS_ICN_WIDTH / 2)+1,
        CROSS_ICN_WIDTH,
        CROSS_ICN_WIDTH,
        1
    )

    # Centered cross notice:
    if abs(Control.y) < 0.01 and abs(Control.r) < 0.01:
        plat.display.text("+", 0, 0)

    # Control gain display:
    plat.display.text("Y:{} R:{}".format(Control.g_y, Control.g_r), 72, 2)

    plat.display.show()  # PUSH to hardware


# # MESSAGING / TRANSMISSION
def send_control():
    pak = plat.c.gen_message(
        recp_id=0,  # Intended recipient ID
        codec_id=1,  # Codec ID
        sub_id=0,  # Message packet sub ID
        max_id=bytes([0]),  # Maximum number of packets in message
        body=Control.gen_control_string()
    )
    plat.radio.send(pak.to_raw)


def main():
    tx_timer = None
    try:
        plat.setup()
        while plat.running:
            loop_start = time.ticks_ms()  # Loop timer

            button_detect()
            update_display()

            if tx_timer is None or time.ticks_diff(time.ticks_ms(), tx_timer) >= TX_PERIOD:
                send_control()
                tx_timer = time.ticks_ms()
            else:  # Only sleep if no tx occurred
                # Handle loop sleep, based on elapsed time:
                t_elapsed = time.ticks_diff(time.ticks_ms(), loop_start)
                sleep = LOOP_PERIOD - t_elapsed
                if sleep > 0:
                    time.sleep_ms(sleep)
                else:
                    print("CLOCK STRETCHING ", sleep)
    finally:
        plat.close()
