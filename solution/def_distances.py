from solution.std_lib import *
import math

debug = 1


def def_distances(particle):
    if debug:
        print("\n***************************************************************")
        print(" Before P", particle.number, "own distance", particle.own_dist, "coords", particle.coords)

    nh_list = scan_nh(particle)

    for dir in direction:
        nh_list[dir].dist = get_nh_dist(dir, nh_list[dir].type, particle.rcv_buf)

    if debug :
        print("Direction | Type | Distance")
        for dir in direction:
            print(dir_to_str(dir), "|", nh_list[dir].type, "|", nh_list[dir].dist)
            #print("Neighborhood distance list", nh_list.values())
    particle.own_dist = calc_own_dist(nh_list)

    if particle.own_dist != math.inf:
        for dir in direction:
            nh_list[dir].dist = calc_nh_dist(dir, nh_list, particle.own_dist)
            #if particle is beside a tile then this tile is the new target
            if nh_list[dir].type == "t":
                particle.dest_t == particle.get_tile_in(dir)
        return nh_list
    return False
def scan_nh(particle):
    nh_list = list()
    for dir in direction:
        if particle.particle_in(dir):
            nh_list.append(Neighbors("p", math.inf))
        elif particle.tile_in(dir):
            nh_list.append(Neighbors("t", 0))
        else:
            nh_list.append(Neighbors("fl", math.inf))
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
    elif type == "p":
        if dir in rcv_buf:
            return rcv_buf[dir].own_dist
    return math.inf


def calc_own_dist(nh_list):
    """
    :param nh_list: A dictionary formed as  {dir_1: "dist_1", ..., dir_6: "dist_6"}
    :return: The own distance of the the particle
    """
    nh_dist_list = list()
    for dir in direction:
        nh_dist_list.append(nh_list[dir].dist)
    min_nh_dist = min(nh_dist_list)
    return  min_nh_dist + 1


def calc_own_dist_t(nh_list):
    """
    :param nh_list: A dictionary formed as  {dir_1: "dist_1", ..., dir_6: "dist_6"}
    :return: The own distance of the the particle
    """
    if nh_list.type == "tile":
        return 1
    return math.inf

def calc_nh_dist(dir, nh_list, own_dist):
    if nh_list[dir].dist is math.inf and \
            (own_dist != math.inf or \
             nh_list[dir_in_range(dir + 1)].dist != math.inf or \
             nh_list[dir_in_range(dir - 1)].dist != math.inf):
        # """
        # if the defined direction is a FL and in SE, SW, NW, NE and the min dist is coming
        #  from one of those direction than the fl becomes the same distance
        # """
        if nh_list[dir].type == "fl" and dir in [SE, SW, NE, NW]:
            min_dir = min ([dir_in_range(dir + 1), dir_in_range(dir - 1)], key=(lambda k:  nh_list[k].dist) )
            if min_dir in [SE, SW, NE, NW]:
                if nh_list[min_dir].dist < own_dist and nh_list[min_dir].dist != 0:
                    return nh_list[min_dir].dist
        return 1 + min(own_dist,
                       nh_list[dir_in_range(dir + 1)].dist,
                       nh_list[dir_in_range(dir - 1)].dist)

    return nh_list[dir].dist