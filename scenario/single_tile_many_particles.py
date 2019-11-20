from lib.swarm_sim_header import *

max = 30


def scenario(sim):
    sim.add_tile(0.0, 0.0)
    generating_random_spraded_particles(sim, max)
