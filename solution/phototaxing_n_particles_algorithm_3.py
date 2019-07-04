import logging
import random

from lib.particle_graph import ParticleGraph
from lib.utils import Utils

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5


direction = [NE, E, SE, SW, W, NW]


def solution(sim):

    for particle in sim.get_particle_list():
        utils = Utils()
        # For every particle in every round, the light beams need to be retraced first
        delete_light_information(sim)
        init_full_light_propagation(sim)

        # Scanning for the particles in the vicinity
        neighbor_list = particle.scan_for_particle_in(1)
        neighbor_list_2 = particle.scan_for_particle_within(2)

        nb_l1 = neighbor_list
        nb_l2 = []

        dir_l2 = random.choice([0, 1, 2, 3, 4, 5])
        can_move = True

        if neighbor_list is None or len(neighbor_list) == 6:
            can_move = False
        else:
            for nb in neighbor_list:
                if determine_direction_from_coords(particle.coords, nb.coords) == dir_l2:
                    can_move = False
                    break
            coords = determine_coords_from_direction(particle.coords, dir_l2)
            for dir in range(0, 6):
                loc_coords = determine_coords_from_direction(coords, dir)
                for nb in neighbor_list_2:
                    if utils.compare_coords(loc_coords, nb.coords):
                        nb_l2.append(nb)

        if can_move:
            particle_graph = ParticleGraph()
            particle_graph.create_neighbor_graph(sim, particle, nb_l1)

            location_graph = ParticleGraph()
            location_graph.create_neighbor_graph(sim, None, nb_l2, determine_coords_from_direction(particle.coords, dir_l2), empty=True)

            if len(neighbor_list) < 5:
                if check_properties(nb_l1, nb_l2, particle_graph, location_graph):
                    particle.move_to(dir_l2)


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

    if x < 25:
        if potential_tile is None and potential_particle is None:
            light_propagation(sim, x, y, dirval)
        elif potential_particle is not None:
            # print("found")
            potential_particle.write_memory_with("light", 1)


# Refer to phototaxing_2_particles_algorithm.py for documentation
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


# Refer to phototaxing_2_particles_algorithm.py for documentation
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


#
def check_properties(particle_neighbors, location_neighbors, particle_graph, location_graph):
    common_list = []
    for nb1 in particle_neighbors:
        for nb2 in location_neighbors:
            if nb1 == nb2:
                common_list.append(nb1)
    print(len(common_list))

    if len(common_list) == 0:
        if len(particle_neighbors) > 0 and len(location_neighbors) > 0:
            if len(particle_graph.list_particles) > 0:
                start_node = particle_graph.list_particles[0]
            particle_graph.run_search_from(start_node, visit=1)

            if len(location_graph.list_particles) > 0:
                start_node = location_graph.list_particles[0]
            location_graph.run_search_from(start_node, visit=1)

            if particle_graph.check_visited() and location_graph.check_visisted():
                print("Condition 2 check")
                return True
        else:
            return False
    elif len(common_list) == 1 or len(common_list) == 2:
        particle_graph.merge_graphs_at(location_graph)
        if len(particle_graph.list_particles) > 0:
            start_node = particle_graph.list_particles[0]
        particle_graph.run_search_from(start_node, visit=1)
        if particle_graph.check_visited():
            print("Condition 1 check")
            return True
        else:
            return False
    return False


