from lib.swarm_sim_header import *
import math


def def_distances(particle):
    if debug and debug_distance_calculation:
        print("\n***************************************************************")
        print(" Before P", particle.number, "own distance", particle.own_dist, "coords", particle.coords)

    nh_list = scan_nh(particle)

    for dir in direction_list:
        nh_list[dir].dist = get_nh_dist(dir, nh_list[dir].type, particle.rcv_buf)

    if debug and debug_distance_calculation:
        print("Direction | Type | Distance")
        for dir in direction_list:
            print(direction_number_to_string(dir), "|", nh_list[dir].type, "|", nh_list[dir].dist)
            #print("Neighborhood distance list", nh_list.values())
    particle.own_dist = calc_own_dist(nh_list)
    if particle.own_dist != math.inf:
        for dir in direction_list:
            nh_list[dir].dist = calc_nh_dist(dir, nh_list, particle.own_dist)
            #if particle is beside a tile then this tile is the new target
            if nh_list[dir].type == "t":
                particle.dest_t = particle.get_tile_in(dir)
    if "fl" not in list(map(lambda neighbor: neighbor.type, nh_list)):
        particle.keep_distance = True
    return nh_list


def scan_nh(particle):
    nh_list = []
    for dir in direction_list:
        if particle.particle_in(dir):
            nh_list.append(Neighbor("p", math.inf))
        elif particle.tile_in(dir):
            nh_list.append(Neighbor("t", 0))
        else:
            nh_list.append(Neighbor("fl", math.inf))
    return nh_list


def get_nh_dist(dir, type, rcv_buf):
    """
    :param type: The type of the neighborhood matter
    :param rcv_buf: The receiver buffer that is a dictionary as {dir, dist} and keeps t
                    he dir and dist of adjacent particle
    :return: The distance of the adjacent node
    """
    if type == "t":
        return 0
    if dir in rcv_buf:
        return rcv_buf[dir].own_dist
    return math.inf


def calc_own_dist(nh_list):
    """
    :param nh_list: A dictionary formed as  {dir_1: "dist_1", ..., dir_6: "dist_6"}
    :return: The own distance of the the particle
    """
    nh_dist_list = list() # nh_dist_list = [neighbor.dist for neightbor in nh_list]
    for dir in direction_list:
        nh_dist_list.append(nh_list[dir].dist)
    min_nh_dist = min(nh_dist_list)
    return min_nh_dist + 1


def calc_own_dist_t(matter):
    """
    :param matter: A dictionary formed as  {dir_1: "dist_1", ..., dir_6: "dist_6"}
    :return: The own distance of the the particle
    """
    if matter.type == "tile":
        return 1
    return math.inf


def calc_nh_dist(dir, nh_list, own_dist):
    if nh_list[dir].dist is math.inf and \
            (own_dist != math.inf or
             nh_list[direction_in_range(dir + 1)].dist != math.inf or
             nh_list[direction_in_range(dir - 1)].dist != math.inf):
        # """
        # if the defined direction is a FL and in SE, SW, NW, NE and the min dist is coming
        #  from one of those direction than the fl becomes the same distance
        # """
        if nh_list[dir].type == "fl" and nh_list[dir].dist == math.inf and dir in [SE, SW, NE, NW]:
            min_dir = min([direction_in_range(dir + 1), direction_in_range(dir - 1)], key=(lambda k:  nh_list[k].dist))
            if min_dir in [SE, SW, NE, NW]:
                if nh_list[min_dir].dist < own_dist and nh_list[min_dir].dist != 0:
                    return nh_list[min_dir].dist
        return 1 + min(own_dist,
                       nh_list[direction_in_range(dir + 1)].dist,
                       nh_list[direction_in_range(dir - 1)].dist)

    return nh_list[dir].dist