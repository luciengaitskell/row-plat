from typing import Union


class PWMInterface:
    def __init__(self, freq: Union[callable, int], gain: float=1.):
        self.freq = freq
        self.gain = gain

    def set_pwm_freq(self, freq_hz):  # Frequency in hertz
        raise NotImplementedError

    def _set_pwm(self, ms):
        raise NotImplementedError

    def get_freq(self):
        if callable(self.freq):
            return self.freq()
        else:
            return self.freq

    def set_pwm_ms(self, ms):  # PWM time in milliseconds
        f = self.get_freq()
        ms *= self.gain

        if ms/1000 > (1/f):  # Check if time is higher than frequency allows
            raise ValueError("PWM time higher than frequency allows.")
        elif ms < 0:
            raise ValueError("PWM time is less than 0.")

        self._set_pwm(ms)
