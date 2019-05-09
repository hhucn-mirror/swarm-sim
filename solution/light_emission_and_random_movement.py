import random

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5


direction = [NE, E, SE, SW, W, NW]


def solution(sim):
    # For every round/iteration, the light key needs to be erased for every particle
    for particle in sim.get_particle_list():
        if particle.read_memory_with("light") is not None:
            particle.delete_memeory_with("light")

    # All light emitting tiles should execute the light propagation algorithm
    for tile in sim.get_tiles_list():
        dirval = tile.read_memory_with("light_emission")
        if dirval is not None:
            light_propagation(sim, tile.coords[0], tile.coords[1], dirval)

    # If the individual particle senses light, it should move randomly
    for particle in sim.get_particle_list():
        if particle.read_memory_with("light") is not None:
            particle.move_to(random.choice(direction))


# This is the light emission algorithm, takes the coordinates
# for where to start and the direction in which to propagate
def light_propagation(sim, x, y, dirval):

    # IMPORTANT: These are the directions for light propagation, they add N and S as possible directions
    # For each direction, the coordinates are adjusted to look to the next position
    if dirval == 0:
        y = y+2
    elif dirval == 1:
        x = x + 0.5
        y = y + 1
    elif dirval == 2:
        x = x + 1
    elif dirval == 3:
        x = x + 0.5
        y = y + 1
    elif dirval == 4:
        y = y - 2
    elif dirval == 5:
        x = x - 0.5
        y = y - 1
    elif dirval == 6:
        x = x + 1
    elif dirval == 7:
        x = x - 0.5
        y = y + 1

    coords = (x, y)

    # Takes the (potential) tile from the sim
    tile_dict = sim.get_tile_map_coords()
    potential_tile = tile_dict.get(coords, None)

    # Takes the (potential) particle from the sim
    particle_dict = sim.get_particle_map_coords()
    potential_particle = particle_dict.get(coords, None)

    if y < 10:  # Just an arbitrary TTL value to limit the simulation
        # If the space is vacant (no particle or tile), propagate further
        if potential_tile is None and potential_particle is None:
            light_propagation(sim, x, y, dirval)
        # If there is a particle on the position, tell it that it senses light
        # The stop condition for reaching a tile is implicitly included, as the algorithm just stops
        elif potential_particle is not None:
            print("found")
            potential_particle.write_memory_with("light", 1)

