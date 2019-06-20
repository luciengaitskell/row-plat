import numpy as np

from rowplat.motion.navigation import Navigation
from rowplat.motion.platform import Platform
from rowplat.motion.position import Position
from sim.impl.simplelocalizer import SimpleLocalizer
from sim.impl.simplepathalg import SimplePathAlg
from sim.impl.simplethruster import SimpleThruster
from sim.impl.simplewaypointhandler import SimpleWaypointHandler
from sim.impl.target import Target
from sim.plot import Plot

STEP = 0.01

p = Plot()

thr = [
    SimpleThruster(Position(-0.25, -0.25, 0)),
    SimpleThruster(Position(0.25, -0.25, 0))
]

plat = Platform(thr)
alg = SimplePathAlg(0.25, 3, 0.1, 2*np.pi/180., 0.6, 0.3)
tar = Target(Position(0., 5., rot=0.))
wyp = SimpleWaypointHandler(target=tar)
loc = SimpleLocalizer(plat=plat)
nav = Navigation(plat=plat, pos=loc, wyp=wyp, alg=alg)

while True:
    p.boat = loc.current
    p.waypoint = wyp.waypoint
    p.target = tar.pos

    p.update(0.01)

    nav.frame()
    loc.frame(STEP)
    tar.frame(STEP)
    print(plat.last_thrust)
