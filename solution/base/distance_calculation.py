from lib.swarm_sim_header import *
import math
from solution import solution_header


def calculate_distances(particle):
    if debug and debug_distance_calculation:
        print("\n***************************************************************")
        print(" Before P", particle.number, "own distance", particle.own_dist, "coords", particle.coords)

    nh_list = scan_nh(particle)

    for direction in direction_list:
        nh_list[direction].dist = get_nh_dist(direction, nh_list[direction].type, particle.rcv_buf)

    if debug and debug_distance_calculation:
        print("Direction | Type | Distance")
        for direction in direction_list:
            print(direction_number_to_string(direction), "|", nh_list[direction].type, "|", nh_list[direction].dist)

    particle.own_dist = calc_own_dist(nh_list)
    # recalculate unknown neighbor distances based on own distance
    if particle.own_dist != math.inf:
        for direction in direction_list:
            nh_list[direction].dist = calc_nh_dist(direction, nh_list, particle.own_dist)
            #if particle is beside a tile then this tile is the new target
            if nh_list[direction].type == "t":
                particle.dest_t = particle.get_tile_in(direction).coordinates
    return nh_list


def scan_nh(particle):
    """
    Scans all directions for the type of neighbor they contain
    :param particle: the particle whose neighborhood to check
    :return: the new neighborhood list
    """
    nh_list = []
    for direction in direction_list:
        if particle.particle_in(direction):
            nh_list.append(solution_header.Neighbor("p", math.inf))
        elif particle.tile_in(direction):
            nh_list.append(solution_header.Neighbor("t", 0))
        else:
            nh_list.append(solution_header.Neighbor("fl", math.inf))
    return nh_list


def get_nh_dist(direction, type, rcv_buf):
    """
    Checks received messages for distance information of neighbors
    :param direction: direction of the neighbor
    :param type: The type of the neighbor
    :param rcv_buf: the messages containing distance information
    :return: The distance of the neighbor
    """
    if type == "t":
        return 0
    elif direction in rcv_buf and isinstance(rcv_buf[direction], solution_header.OwnDistance):
        return rcv_buf[direction].particle_distance
    return math.inf


def calc_own_dist(nh_list):
    """
    calculates a particles own distance
    :param nh_list: the neighborhood of the particle
    :return: The own distance of the the particle
    """
    min_nh_dist = min([neighbor.dist for neighbor in nh_list])
    return min_nh_dist + 1


def calc_own_dist_t(matter):
    """
    If a tile is in a particles neighborhood it's distance is always 1
    :param matter: any matter in the particles neighborhood
    :return: The own distance of the the particle
    """
    if matter.type == "tile":
        return 1
    return math.inf


def calc_nh_dist(direction, nh_list, own_dist):
    """
    Calculates the distance of a neighbor based on own distance
    :param direction: the direction of the neighbor
    :param nh_list: the particles neighborhood
    :param own_dist: the particles own distance
    :return: the estimated distance of the neighbor
    """
    if own_dist != math.inf:
        estimated_distance = 1 + min(own_dist,
                                     nh_list[direction_in_range(direction + 1)].dist,
                                     nh_list[direction_in_range(direction - 1)].dist)
        if estimated_distance < nh_list[direction].dist:
            return estimated_distance
    return nh_list[direction].dist
