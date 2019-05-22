from sparksim import Spark, App, simulate
from schedulers import EDFAll, EDFPure, Fair, FIFO


scale = 1

apps = [App(1, 60//scale, 300//scale), App(2, 86//scale, 300//scale), App(3, 77//scale, 120//scale)]

init = Spark(EDFPure(), {apps[0] : (1, 0)}, {})

simulate(init, apps, steps)

init = Spark(EDFAll(), {apps[0] : (1, 0)}, {})

simulate(init, apps, steps)

init = Spark(FIFO(), {apps[0] : (1, 0)}, {})

simulate(init, apps, steps)

init = Spark(Fair(), {apps[0] : (1, 0)}, {})

simulate(init, apps)
