import RPi.GPIO as GPIO

from ..base.interface import PWMInterface
from ..base.motor import Motor


class MD10C(Motor):
    def __init__(self, pwm_i: PWMInterface, gpio_pin):
        self.i = pwm_i
        self.pin = gpio_pin
        GPIO.setup(gpio_pin, GPIO.OUT)

    def _set_motor_power(self, p: float):
        # Set DIR pin:
        if p < 0:
            GPIO.output(self.pin, GPIO.HIGH)
        elif p >= 0:
            GPIO.output(self.pin, GPIO.LOW)

        # Set freq:
        max_v = (1/self.i.get_freq())*1000
        self.i.set_pwm_ms(max_v * abs(p))
