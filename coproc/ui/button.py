from machine import Pin


class Button:
    def __init__(self, pin: Pin = None, last=False):
        self.pin = pin  # Callable/Function to get status of button
        self._last = last  # Last (default in this case) button value

    @property
    def last(self):
        """ Get last value of button. """
        return self._last

    def update(self, value=None) -> bool:
        """
        Update button tracking.

        :return bool: If button value is new
        """
        if value is None:  # If no value was passed
            value = self.pin.value()  # attempt to read from supplied pin

        ret = not (value == self.last)  # Determine if value differs from last
        self._last = value  # Update saved last value
        return ret

