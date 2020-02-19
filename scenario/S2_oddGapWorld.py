from scenario.particleGroups import *


def scenario(sim):
    #doubleline20(sim)
    #around37(sim)
    #star50(sim)
    block100(sim)

# 3 places diameter
    sim.add_tile(7.5, 1)
    sim.add_tile(11.5, 1)
    sim.add_tile(12.5, -1)
    sim.add_tile(8.5, -1)
    sim.add_tile(8, 0)
    sim.add_tile(12, 0)
    sim.add_tile(9, 2)
    sim.add_tile(10, 2)
    sim.add_tile(8, 2)
    sim.add_tile(11, 2)
    sim.add_tile(7, 2)
