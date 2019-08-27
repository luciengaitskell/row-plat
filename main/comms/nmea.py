import pynmea2


class CTL(pynmea2.TalkerSentence):
    """ Custom
    """
    fields = (
        ("Thruster enable", "en"),
        ("Thruster mode/layout", "tmde"),
        ("Y-axis control", "y"),
        ("Rotational control", "r"),
        ("Y-axis gain", "y_g"),
        ("Rotational gain", "r_g"),
    )

    @property
    def enable(self):
        return self.en == 'True'

    @property
    def mode(self):
        return int(self.tmde)

    @property
    def control_y(self):
        return float(self.y)

    @property
    def control_r(self):
        return float(self.r)

    @property
    def gain_y(self):
        return float(self.y_g)

    @property
    def gain_r(self):
        return float(self.r_g)
