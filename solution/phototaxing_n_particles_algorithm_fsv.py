from solution.particle_graph import check_connectivity_after_move
from solution.utils import *
from solution.goal_params import *

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

    ##########
    for particle in sim.get_particle_list():

        # For every particle in every round, the light beams need to be retraced first
        delete_light_information(sim)
        init_full_light_propagation(sim)

        param_lambda = sim.param_lambda
        param_delta = sim.param_delta
        #If this is not a multiple simulation, the params can be adjusted here
        if not sim.multiple:
            param_lambda = 5
            param_delta = 1

        phototaxing_fsv(param_delta, param_lambda, particle)

# This is the phototaxing algorithm
#
def phototaxing_fsv(param_delta, param_lambda, particle):
    # Scanning for the particles in the vicinity
    immediate_neighbors = particle.scan_for_particle_in(1)
    if immediate_neighbors is not None:
        old_pos_edges = len(immediate_neighbors)
    neighbor_list = particle.scan_for_particle_within(2)
    can_move = True
    # The algorithm continues only if the particle has less than six neighbors
    if immediate_neighbors is not None and len(immediate_neighbors) < 6:
        move_direction = determine_choice_from_vacant_positions(immediate_neighbors, particle)
        # The algorithm stops if the new position is occupied by a tile
        can_move = check_if_tile_occupies_pos(move_direction, particle)
    else:
        can_move = False
    if can_move:
        # This returns a boolean (is the graph locally connected?) and the neighbor edges at the new position
        connectivity_and_edges = check_connectivity_after_move(particle.coords, neighbor_list, move_direction)
        if connectivity_and_edges[0]:
            new_pos_edges = connectivity_and_edges[1]
            if (new_pos_edges - old_pos_edges > param_delta and particle.read_memory_with("light") is not None) or random.randint(0,
                                                                                                                param_lambda - 1) == 0:
                particle.move_to(move_direction)

# Checks if a position in a direction is occupied by a particle
def check_if_tile_occupies_pos(move_direction, particle):
    tiles = particle.scan_for_tile_in(1)
    if tiles is not None:
        for tile in tiles:
            if determine_direction_from_coords(particle.coords, tile.coords) == move_direction:
                return False
    return True

# This determines a direction for the particle to move to, of all the vacant positions in the 1-neighborhood
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
    direction_new_position = random.choice(possible_choices)
    return direction_new_position
