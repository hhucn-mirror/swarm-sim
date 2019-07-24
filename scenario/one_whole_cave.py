from scenario.scenario_std_lib import *


max = 100


def scenario(sim):
    sim.add_tile(0.0, 2.0)
    sim.add_tile(3.0, 2.0)
    sim.add_tile(0.5, 3.0)
    sim.add_tile(1.5, 3.0)
    sim.add_tile(2.5, 3.0)
    sim.add_tile(3.5, 1.0)
    sim.add_tile(3.0, 0.0)
    sim.add_tile(0.0, 0.0)
    sim.add_tile(-0.5, 1.0)

    generating_random_spraded_particles(sim, max)
