import random
max=500
def scenario(sim):
    sim.add_tile(-0.0, 0.0)
    sim.add_tile(-1.0, 0.0)
    sim.add_tile(-2.0, 0.0)
    sim.add_tile(-3.0, 0.0)
    sim.add_tile(-4.0, 0.0)
    sim.add_tile(-5.0, -0.0)
    sim.add_tile(-6.0, -0.0)
    sim.add_tile(-7.0, 0.0)
    #sim.add_tile(-8.0, 0.0)

    for _ in range(0, max):
        x = random.randrange(-sim.get_sim_x_size(), sim.get_sim_x_size())
        y = random.randrange(-sim.get_sim_y_size(), sim.get_sim_y_size())
        if y % 2 == 1:
            x = x + 0.5
        if (x, y) not in sim.tile_map_coords:
            sim.add_particle(x, y)
        else:
            print(" x and y ", (x, y))
    print("Max Size of created Particle", len(sim.particles))
    # sim.add_particle(1.5, 1.0)
    # sim.add_particle(0.5, 1.0)
    # sim.add_particle(1.0, -0.0)
    # sim.add_particle(0.5, -1.0)
    # sim.add_particle(1.5, -1.0)
    # sim.add_particle(2.0, 0.0)
    # sim.add_particle(2.5, 1.0)
    # sim.add_particle(2.5, -1.0)