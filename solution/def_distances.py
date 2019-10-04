from lib.swarm_sim_header import *
import math


def def_distances(particle):
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
            #print("Neighborhood distance list", nh_list.values())
    particle.own_dist = calc_own_dist(nh_list)
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
    nh_list = []
    for direction in direction_list:
        if particle.particle_in(direction):
            nh_list.append(Neighbor("p", math.inf))
        elif particle.tile_in(direction):
            nh_list.append(Neighbor("t", 0))
        else:
            nh_list.append(Neighbor("fl", math.inf))
    return nh_list


def get_nh_dist(direction, type, rcv_buf):
    """
    :param direction: direction of the neighborhood matter
    :param type: The type of the neighborhood matter
    :param rcv_buf: The receiver buffer that is a dictionary as {direction, dist} and keeps t
                    he direction and dist of adjacent particle
    :return: The distance of the adjacent node
    """
    if type == "t":
        return 0
    if direction in rcv_buf:
        return rcv_buf[direction].particle_distance
    return math.inf


def calc_own_dist(nh_list):
    """
    :param nh_list: A dictionary formed as  {direction_1: "dist_1", ..., direction_6: "dist_6"}
    :return: The own distance of the the particle
    """
    nh_dist_list = list() # nh_dist_list = [neighbor.dist for neightbor in nh_list]
    for direction in direction_list:
        nh_dist_list.append(nh_list[direction].dist)
    min_nh_dist = min(nh_dist_list)
    return min_nh_dist + 1


def calc_own_dist_t(matter):
    """
    :param matter: A dictionary formed as  {direction_1: "dist_1", ..., direction_6: "dist_6"}
    :return: The own distance of the the particle
    """
    if matter.type == "tile":
        return 1
    return math.inf


def calc_nh_dist(direction, nh_list, own_dist):
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
