import random

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5


direction = [NE, E, SE, SW, W, NW]


def solution(sim):
    # Erase the light memory at every round start
    for particle in sim.get_particle_list():
        if particle.read_memory_with("light") is not None:
            particle.delete_memeory_with("light")

    # Calculate the light emission for the new round
    for tile in sim.get_tiles_list():
        dirval = tile.read_memory_with("light_emission")
        if dirval is not None:
            light_propagation(sim, tile.coords[0], tile.coords[1], dirval)

    # Algorithm for 2-Particle phototaxing.
    for particle in sim.get_particle_list():
        # Get the neighboring particle's position (If there are <1 or >1 there is something wrong)
        list = particle.scan_for_particle_in(1)
        if list is not None and len(list) == 1:
            # Calculating the possible positions to move to
            direction_of_neighbor = determine_direction_from_coords(particle.coords, list[0].coords)
            possible_locations = [-1, -1]
            possible_locations[0] = (direction_of_neighbor - 1) % 6
            possible_locations[1] = (direction_of_neighbor + 1) % 6

            # If the position is unoccupied, add the position to the choices
            choices = []
            if sim.get_tile_map_coords().get(
                    determine_coords_from_direction(particle.coords, possible_locations[0])) is None:
                choices.insert(0, possible_locations[0])
            if sim.get_tile_map_coords().get(
                    determine_coords_from_direction(particle.coords, possible_locations[1])) is None:
                choices.insert(0, possible_locations[1])

            # If the particle senses light, move to one of the choices
            # If not, move to one of the choices with a 25% probability
            if particle.read_memory_with("light") is not None:
                particle.move_to(random.choice(choices))
            elif random.choice([0, 1, 2, 3]) == 0:
                particle.move_to(random.choice(choices))

# Light propagation algorithm as previously explained in light_emission_and_random_movement.py
def light_propagation(sim, x, y, dirval):

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

    tile_dict = sim.get_tile_map_coords()
    potential_tile = tile_dict.get(coords, None)

    particle_dict = sim.get_particle_map_coords()
    potential_particle = particle_dict.get(coords, None)

    if x < 15:
        if potential_tile is None and potential_particle is None:
            light_propagation(sim, x, y, dirval)
        elif potential_particle is not None:
            potential_particle.write_memory_with("light", 1)


# This algorithm takes two coordinates,
# returns the angle from a to b from the view of a
def determine_direction_from_coords(coords_a, coords_b):
    delta_x = coords_a[0] - coords_b[0]
    delta_y = coords_a[1] - coords_b[1]

    if delta_x == 0 and delta_y == 0:
        return -1
    elif delta_x == -0.5 and delta_y == -1:
        return 0
    elif delta_x == -1 and delta_y == 0:
        return 1
    elif delta_x == -0.5 and delta_y == 1:
        return 2
    elif delta_x == 0.5 and delta_y == 1:
        return 3
    elif delta_x == 1 and delta_y == 0:
        return 4
    elif delta_x == 0.5 and delta_y == -1:
        return 5
    else:
        return -1

# This algorithm takes a coordinate and a direction,
# returns the position that results from moving in that direction
def determine_coords_from_direction(coords, dirval):
    coords_new = (coords[0], coords[1])
    x = coords[0]
    y = coords[1]

    if dirval == 0:
        coords_new = (x + 0.5, y + 1)
    elif dirval == 1:
        coords_new = (x+1, y)
    elif dirval == 2:
        coords_new = (x + 0.5, y - 1)
    elif dirval == 3:
        coords_new = (x - 0.5, y - 1)
    elif dirval == 4:
        coords_new = (x - 1, y)
    elif dirval == 5:
        coords_new = (x - 0.5, y + 1)
    return coords_new
