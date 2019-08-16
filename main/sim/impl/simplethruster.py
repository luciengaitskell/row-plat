from rowplat.abstract.thruster import Thruster


class SimpleThruster(Thruster):
    def __init__(self, pos):
        super().__init__(pos)
        self.curr_pwr = 0

    def _set_power(self, pwr):
        self.curr_pwr = pwr

    def _conv_thrust(self, thrust):
        return thrust  # Pretend power
