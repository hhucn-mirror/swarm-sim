import logging
import random

from lib.particle_graph_2 import ParticleGraph
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
        print(sim.get_actual_round())
        utils = Utils()
        # For every particle in every round, the light beams need to be retraced first
        delete_light_information(sim)
        init_full_light_propagation(sim)

        # Scanning for the particles in the vicinity
        immediate_neighbors = particle.scan_for_particle_in(1)
        particle_edges = len(immediate_neighbors)
        neighbor_list = particle.scan_for_particle_within(2)

        can_move = True
        possible_choices = []
        if immediate_neighbors is not None and len(immediate_neighbors) < 6:
            for dir in range(0, 6):
                coords = utils.determine_coords_from_direction(particle.coords, dir)
                found = False
                for nb in immediate_neighbors:
                    if utils.compare_coords(coords, nb.coords):
                        found = True
                if not found:
                    possible_choices.append(dir)
            dir_l2 = random.choice(possible_choices)

            if neighbor_list is None:
                can_move = False
            else:
                for nb in neighbor_list:
                    if determine_direction_from_coords(particle.coords, nb.coords) == dir_l2:
                        can_move = False
                        break
                tiles = particle.scan_for_tile_in(1)
                if tiles is not None:
                    for tile in particle.scan_for_tile_in(1):
                        if tile.read_memory_with("goal-tile"):
                            print("Successful!")
                            sim.success_termination()
                        if determine_direction_from_coords(particle.coords, tile.coords) == dir_l2:
                            can_move = False
                            break
        else:
            can_move = False

        if can_move:
            particle_graph = ParticleGraph()
            checks = particle_graph.check_connectivity_after_move(particle.coords, neighbor_list, dir_l2)
            if checks[0]:
                new_location_edges = checks[1]
                if new_location_edges - particle_edges > -1 and particle.read_memory_with("light") is not None:
                    particle.move_to(dir_l2)
                elif random.randint(0, 20) == 0:
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


