import random

from lib.particle_graph_2 import check_connectivity_after_move, check_for_connectivity_in_merged_graphs, \
    create_graph, run_search_with_exclusion
from lib.utils import *
from lib.goal_params import *

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5


direction = [NE, E, SE, SW, W, NW]


def solution(sim):
    # Checking if the goal has been reached
    check_all_goal_params(sim)
    avg_coords = [0.0, 0.0]
    for particle in sim.particles:
        avg_coords[0] = avg_coords[0] + particle.coords[0]
        avg_coords[1] = avg_coords[1] + particle.coords[1]
    avg_coords[0] = avg_coords[0] / len(sim.particles)
    avg_coords[1] = avg_coords[1] / len(sim.particles)

    print("X: " + str(avg_coords[0]) + " - " + str(avg_coords[1]))


    ##########
    for particle in sim.get_particle_list():
        lmbd = 4
        # For every particle in every round, the light beams need to be retraced first
        delete_light_information(sim)
        init_full_light_propagation(sim)

        neighbors = particle.scan_for_particle_in(1)
        if len(neighbors) < 5:
            dir_newpos = random.choice([0, 1, 2, 3, 4, 5])
            if check_if_particle_occupies_pos(dir_newpos, particle) and check_if_tile_occupies_pos(dir_newpos, particle):
                newpos = determine_coords_from_direction(particle.coords, dir_newpos)
                neighbors_at_newpos = determine_neighbors_at_vacant_location(particle, dir_newpos)
                triangles = len(neighbors)
                triangles_newpos = len(neighbors_at_newpos)

                properties_checked = check_properties(neighbors, neighbors_at_newpos, particle.coords, newpos)
                q = random.uniform(0, 1)
                equation = lmbd ** (triangles_newpos - triangles)
                if properties_checked and q < equation:
                    if particle.read_memory_with("light") is not None:
                        particle.move_to(dir_newpos)
                    elif random.choice([0, 1, 2, 4]) == 0:
                        particle.move_to(dir_newpos)




def check_if_particle_occupies_pos(move_direction, particle):
    neighbors = particle.scan_for_particle_in(1)
    if neighbors is not None:
        for nb in neighbors:
            if determine_direction_from_coords(particle.coords, nb.coords) == move_direction:
                return False
    return True


def check_if_tile_occupies_pos(move_direction, particle):
    tiles = particle.scan_for_tile_in(1)
    if tiles is not None:
        for tile in tiles:
            if determine_direction_from_coords(particle.coords, tile.coords) == move_direction:
                return False
    return True


def determine_neighbors_at_vacant_location(particle, dir):
    neighbors = []
    all_neighbors = particle.scan_for_particle_within(2)
    coords_loc = determine_coords_from_direction(particle.coords, dir)
    for i in range(0, 6):
        coords_nb = determine_coords_from_direction(coords_loc, i)
        for nb in all_neighbors:
            if compare_coords(nb.coords, coords_nb):
                neighbors.append(nb)
    return neighbors


def determine_choice_from_vacant_positions(immediate_neighbors, particle):
    possible_choices = []
    for dir in range(0, 6):
        coords = determine_coords_from_direction(particle.coords, dir)
        found = False
        for nb in immediate_neighbors:
            if compare_coords(coords, nb.coords):
                found = True
        if not found:
            possible_choices.append(dir)
    dir_l2 = random.choice(possible_choices)
    return dir_l2


def check_properties(particle_neighbors, location_neighbors, particle_coords, location_coords):
    common_list = []
    for nb1 in particle_neighbors:
        for nb2 in location_neighbors:
            if nb1 == nb2:
                common_list.append(nb1)

    graph1 = create_graph(particle_neighbors)
    graph2 = create_graph(location_neighbors)
    if len(common_list) == 0:
        if len(particle_neighbors) > 0 and len(location_neighbors) > 0:
            check = run_search_with_exclusion(graph1[0], location_coords) \
                    and run_search_with_exclusion(graph2[0], particle_coords)
            return check
    elif len(common_list) == 1 or len(common_list) == 2:
        return check_for_connectivity_in_merged_graphs(particle_neighbors, location_neighbors)
    return False


