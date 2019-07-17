from lib.tile import gray, blue, red, black


def scenario(sim):
    # This creates the initial tiles in the middle (y-axis)
    sim.add_tile(10, 20, color=gray)
    sim.add_tile(20, 0, color=blue)
    sim.add_tile(10, -20, color=gray)
    sim.add_tile(-10, -20, color=gray)
    sim.add_tile(-20, 0, color=red)
    sim.add_tile(-10, 20, color=gray)

    for i in range(1, 20):
        sim.add_tile(-10 + i, 20, color=gray)
        sim.add_tile(10 + (0.5*i), 20 - i, color=blue)
        sim.add_tile(10 + (0.5*i), -20 + i, color=blue)
        sim.add_tile(-10 + i, -20, color=gray)
        sim.add_tile(-10 - (0.5*i), -20 + i, color=red)
        sim.add_tile(-10 - (0.5*i), 20 - i, color=red)

    for tile in sim.tiles:
        if tile.color == [0.8, 0.0, 0.0]:
            tile.write_memory_with("light_emission", 2)
        elif tile.color == [0.0, 0.0, 0.8]:
            tile.write_memory_with("goal-tile", 1)

    # Now we add the particles
    radius = 3
    sim.add_particle(0,0, color=red)
    displacement = - radius + 0.5
    iteration = 0
    for i in range(1, radius+1):
        sim.add_particle( i, 0)
        sim.add_particle(-i, 0)
    for i in range(1, radius+1):
        for j in range(0, (2*radius) - iteration):
            sim.add_particle(displacement + j, i)
            sim.add_particle(displacement + j, -i)
        iteration = iteration + 1
        displacement = displacement + 0.5





    """sim.add_particle(0, 0, color=red)
    sim.add_particle(-1, 0, color=blue)
    sim.add_particle(-2, 0, color=black)
    sim.add_particle(-0.5, 1, color=red)
    sim.add_particle(-1.5, 1, color=blue)
    sim.add_particle(-2.5, 1, color=black)
    sim.add_location(0, 0)"""
