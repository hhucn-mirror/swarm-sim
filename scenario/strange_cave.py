from lib.swarm_sim_header import *

max = 60


def scenario(sim):
    sim.add_tile(0.0, 0.0)
    sim.add_tile(-0.5, -1.0)
    sim.add_tile(-1.5, -1.0)
    sim.add_tile(-2.5, -1.0)
    sim.add_tile(-3.0, -2.0)
    sim.add_tile(-2.5, -3.0)
    sim.add_tile(-3.0, -4.0)
    sim.add_tile(-2.5, -5.0)
    sim.add_tile(-2.0, -6.0)
    sim.add_tile(-1.0, -6.0)
    sim.add_tile(0.0, -6.0)
    sim.add_tile(2.0, -6.0)
    sim.add_tile(1.0, -6.0)
    sim.add_tile(3.0, -6.0)
    sim.add_tile(4.0, -6.0)
    sim.add_tile(5.0, -6.0)
    sim.add_tile(6.0, -6.0)
    sim.add_tile(7.5, -5.0)
    sim.add_tile(7.0, -6.0)
    sim.add_tile(7.0, -4.0)
    sim.add_tile(6.5, -3.0)
    sim.add_tile(5.0, -2.0)
    sim.add_tile(6.0, -2.0)
    sim.add_tile(4.5, -1.0)
    sim.add_tile(4.0, 0.0)
    sim.add_tile(3.0, 0.0)
    sim.add_tile(2.0, 0.0)
    generating_random_spraded_particles(sim, max)