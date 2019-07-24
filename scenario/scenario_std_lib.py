import random

#colors
black = 1
gray = 2
red = 3
green = 4
blue = 5
yellow = 6
orange = 7
cyan = 8
violett = 9


#directions
NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5

direction = [NE, E, SE, SW, W, NW]

def generating_random_spraded_particles (sim, max_size_particle):
    for _ in range(0, max_size_particle):
        x = random.randrange(-sim.get_sim_x_size(), sim.get_sim_x_size())
        y = random.randrange(-sim.get_sim_y_size(), sim.get_sim_y_size())
        if y % 2 == 1:
            x = x + 0.5
        if (x, y) not in sim.tile_map_coords:
            sim.add_particle(x, y)
        else:
            print(" x and y ", (x, y))
    print("Max Size of created Particle", len(sim.particles))

def create_particle_in_line(sim, max_size_particle):
    max_x = -1000000
    for tile in sim.tiles:
        if tile.coords[0] > max_x:
            max_x = tile.coords[0]
            coords = tile.coords
    if coords[0] % 1 != 0:
        start_i = int(coords[0] - 0.5)
        for i in range(start_i, start_i+max_size_particle):
            sim.add_particle(i + 1.5, coords[1])

    else:
        for i in range(int(coords[0] + 1), int(coords[0] + 1) + max_size_particle):
            sim.add_particle(i, coords[1])
