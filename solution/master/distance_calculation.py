from lib.swarm_sim_header import *
import math
from solution import solution_header


def calculate_distances(particle):
    if debug and debug_distance_calculation:
        print("\n***************************************************************")
        print(" Before P", particle.number, "own distance", particle.own_dist, "coords", particle.coords)

    # detect the types of all neighbors
    nh_list = scan_nh(particle)
    # check received messages for distance information
    for direction in direction_list:
        nh_list[direction].dist = get_nh_dist(direction, nh_list[direction].type, particle.rcv_buf)

    if debug and debug_distance_calculation:
        print("Direction | Type | Distance")
        for direction in direction_list:
            print(direction_number_to_string(direction), "|", nh_list[direction].type, "|", nh_list[direction].dist)
            #print("Neighborhood distance list", nh_list.values())
    # calculate own distance
    particle.own_dist = calc_own_dist(nh_list)
    # recalculate unknown neighbor distances based on own distance
    if particle.own_dist != math.inf:
        for direction in direction_list:
            nh_list[direction].dist = calc_nh_dist(direction, nh_list, particle.own_dist)
            #if particle is beside a tile then this tile is the new target
            if nh_list[direction].type == "t":
                particle.dest_t = particle.get_tile_in(direction)
    if "fl" not in list(map(lambda neighbor: neighbor.type, nh_list)):
        particle.keep_distance = True
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
    if direction in rcv_buf:
        return rcv_buf[direction].particle_distance
    return math.inf


def calc_own_dist(nh_list):
    """
    calculates a particles own distance
    :param nh_list: the neighborhood of the particle
    :return: The own distance of the the particle
    """
    nh_dist_list = list() # nh_list = [neighbor.dist for neightbor in nh_list]
    for direction in direction_list:
        nh_dist_list.append(nh_list[direction].dist)
    min_nh_dist = min(nh_dist_list)
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
    if nh_list[direction].dist is math.inf and \
            (own_dist != math.inf or
             nh_list[direction_in_range(direction + 1)].dist != math.inf or
             nh_list[direction_in_range(direction - 1)].dist != math.inf):
        # """
        # if the defined direction is a FL and in SE, SW, NW, NE and the min dist is coming
        #  from one of those direction than the fl becomes the same distance
        # """
        if nh_list[direction].type == "fl" and nh_list[direction].dist == math.inf and direction in [SE, SW, NE, NW]:
            min_direction = min([direction_in_range(direction + 1), direction_in_range(direction - 1)], key=(lambda k:  nh_list[k].dist))
            if min_direction in [SE, SW, NE, NW]:
                if nh_list[min_direction].dist < own_dist and nh_list[min_direction].dist != 0:
                    return nh_list[min_direction].dist
        return 1 + min(own_dist,
                       nh_list[direction_in_range(direction + 1)].dist,
                       nh_list[direction_in_range(direction - 1)].dist)

    return nh_list[direction].dist
