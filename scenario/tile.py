import copy

E = 0
SE = 1
SW = 2
W = 3
NW = 4
NE = 5
S = 6  # S for stop and not south

direction = [E, SE, SW, W, NW, NE]

def scenario(sim):
    sim.add_tile(0, 0)



    sim.add_particle (1.0, 0.0)
    # sim.add_particle(0.5, 1.0)
    # sim.add_particle(-0.5, 1.0)
    # sim.add_particle(-2.0, -0.0)
    # sim.add_particle(-1.0, -0.0)
    # sim.add_particle(-0.5, -1.0)
    # sim.add_particle(0.5, -1.0)


    # sim.add_particle  (1.5, 1.0)
    sim.add_particle  (2.0, 0.0)
    # sim.add_particle  (2.5, 1.0)
    sim.add_particle  (3.0, -0.0)
    # sim.add_particle  (3.5, 1.0)
    sim.add_particle  (4.0, -0.0)


    # sim.add_particle(1.5, 1.0)
    # sim.add_particle(0.5, 1.0)
    # sim.add_particle(1.0, -0.0)
    # sim.add_particle(0.5, -1.0)
    # sim.add_particle(1.5, -1.0)
    # sim.add_particle(2.0, 0.0)
    # sim.add_particle(2.5, 1.0)
    # sim.add_particle(2.5, -1.0)
