

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


def compare_coords(coords_a, coords_b):
    if len(coords_a) == 2 and len(coords_b) == 2:
        if coords_a[0] == coords_b[0] and coords_a[1] == coords_b[1]:
            return True

    return False


def inv_dir(dir):
    return (dir+3) % 6


# Deletes all the light-entries in the particles to make a fresh start
def delete_light_information(sim):
    for particle in sim.get_particle_list():
        if particle.read_memory_with("light") is not None:
            particle.delete_memeory_with("light")


# Initializes the light propagation. Checks each tile for the light-emission entry and starts the algorithm
def init_full_light_propagation(sim):
    for tile in sim.get_tiles_list():
        dirval = tile.read_memory_with("light_emission")
        if dirval is not None:
            # print("SEARCHING: ", dirval)
            light_propagation(sim, tile.coords[0], tile.coords[1], dirval)


# Refer to light_emission_and_random_movement.py for documentation
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

    if x < 35:
        if potential_tile is None and potential_particle is None:
            light_propagation(sim, x, y, dirval)
        elif potential_particle is not None:
            # print("found")
            potential_particle.write_memory_with("light", 1)


class GoalStateSaver:
    first_particle_passed = False
    half_particles_passed = False
    all_particles_passed = False


class SimulationParamsSaver:
    hexagon_radius = 0
    delta_light = 0
    delta_edges = 0


