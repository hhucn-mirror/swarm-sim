from lib.tile import gray, blue, red, black
import random


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
    amount_x = 5
    amount_y = 2
    sim.add_particle(0, 0, color=red)
    for i in range(0, amount_x):
        for j in range(0, amount_y):
            if j % 2 == 0:
                sim.add_particle(i, j)
                sim.add_particle(-i, j)
                sim.add_particle(i, -j)
                sim.add_particle(-i, -j)
            else:
                sim.add_particle(i+0.5, j)
                sim.add_particle(-i + 0.5, j)
                sim.add_particle(i + 0.5, -j)
                sim.add_particle(-i + 0.5, -j)




    """sim.add_particle(0, 0, color=red)
    sim.add_particle(-1, 0, color=blue)
    sim.add_particle(-2, 0, color=black)
    sim.add_particle(-0.5, 1, color=red)
    sim.add_particle(-1.5, 1, color=blue)
    sim.add_particle(-2.5, 1, color=black)
    sim.add_location(0, 0)"""
