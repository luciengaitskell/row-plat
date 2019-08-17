from rowplat.motion.platform import Platform
from rowplat.motion.position import Position
from sim.impl.simplethruster import SimpleThruster

STEP = 0.01

thr = [
    SimpleThruster(Position(-0.4, -0.25, 0)),
    SimpleThruster(Position(-0.1, -0.25, 0)),
    SimpleThruster(Position(0.1, -0.25, 0)),
    SimpleThruster(Position(0.4, -0.25, 0))
]

plat = Platform(thr)


while True:
    y = float(input("Y: "))
    r = float(input("R: "))
    plat.set_thrust(0, y, r)
    print(plat.last_thrust)
