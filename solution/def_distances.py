from solution.std_lib import *
import math
from solution.read_write import DistInfo

class Neighbors:
    def __init__(self, type, dist):
        self.type = type
        self.dist = dist

    def __str__(self):
        return " " + str(self.type) + " " + str(self.dist)


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
    if particle.own_dist == math.inf:
        particle.own_dist = calc_own_dist(nh_list)
        particle.p_max.id = particle.number
        particle.p_max.dist = particle.own_dist
        particle.p_max.dir = None

    if particle.own_dist != math.inf:
        if not particle.p_max_table:
            particle.p_max_table = {particle.p_max.id: particle.p_max.dist}
        elif particle.number in particle.p_max_table and particle.p_max_table[particle.number] > particle.own_dist:
            particle.p_max_table[particle.number] = particle.own_dist
        for dir in direction:
            nh_list[dir].dist = particle.nh_dist_list[dir] = calc_nh_dist(dir, nh_list, particle.own_dist)
            #if particle is beside a tile then this tile is the new target
            if nh_list[dir].type == "t":
                particle.dest_t == particle.get_tile_in(dir)

        if debug:
            print("Before P MAX:")
            print("id | dist | dir")
            print(particle.p_max)
        particle.p_max_table = find_p_max(particle.p_max, nh_list, particle.rcv_buf, particle.p_max_table)
        particle.p_max_table = update_table(particle.rcv_buf, particle.p_max_table, particle.own_dist)

        if debug:
            print ("P MAX:")
            print("id | dist | dir")
            print(particle.p_max)

    if debug:
        print("\n After P", particle.number, "own distance", particle.own_dist)
        print("Direction | Distance")
        for dir in direction:
            print(dir_to_str(dir),"|", particle.nh_dist_list[dir])
        print("P_Max Table \n ID | Distance")
        for id in particle.p_max_table:
            print (id, "|", particle.p_max_table[id])


def find_p_max(p_max, nh_list, rcv_buf, table):
    #local_p_max(nh_list, p_max)
    table_a = table
    if global_p_max(p_max, rcv_buf):
        if p_max.id not in table:
            max_key = max(table, key=table.get)
            if p_max.dist >= table[max_key]:
                table_a[p_max.id] = p_max.dist

    find_identical(p_max, rcv_buf, table_a)
    return table_a

def global_p_max(p_max, rcv_buf):
    for rcv_dir in rcv_buf:
        if isinstance(rcv_buf[rcv_dir], DistInfo):
            if rcv_buf[rcv_dir].p_max_dist > p_max.dist:
                p_max.id = rcv_buf[rcv_dir].p_max_id
                p_max.dist = rcv_buf[rcv_dir].p_max_dist
                p_max.dir = rcv_dir
                p_max.black_list.clear()
                p_max.black_list.append(rcv_dir)
                return True
    return False


def local_p_max(nh_list, p_max):
    for dir in direction:
        if nh_list[dir].type == "p" and nh_list[dir].dist > p_max.dist:
            p_max.id = None
            p_max.black_list.clear()
            p_max.black_list.append(dir)
            p_max.dist = nh_list[dir].dist
            p_max.dir = dir
            return True
    return False


def find_identical(p_max, rcv_buf, table):
    for rcv_dir in rcv_buf:
        if isinstance(rcv_buf[rcv_dir], DistInfo) and rcv_buf[rcv_dir].p_max_dist == p_max.dist:
            if p_max.id is None:
                p_max.id = rcv_buf[rcv_dir].p_max_id
                p_max.dir = rcv_dir
                if not table:
                    table[p_max.id] = p_max.dist

            if p_max.id != rcv_buf[rcv_dir].p_max_id:
                p_max.black_list.append(rcv_dir)
                if table:
                    table[rcv_buf[rcv_dir].p_max_id] = rcv_buf[rcv_dir].p_max_dist


def update_table(rcv_buf, table, own_dist):
    table_a = table
    for rcv_dir in rcv_buf:
        if isinstance(rcv_buf[rcv_dir], DistInfo):
            if rcv_buf[rcv_dir].own_id in table_a and \
                    rcv_buf[rcv_dir].own_dist < table_a[rcv_buf[rcv_dir].own_id]:
                table_a[rcv_buf[rcv_dir].p_max_id] = rcv_buf[rcv_dir].own_dist
            if rcv_buf[rcv_dir].p_max_id in table_a and \
                rcv_buf[rcv_dir].p_max_dist < table_a[rcv_buf[rcv_dir].p_max_id]:
                table_a[rcv_buf[rcv_dir].p_max_id] = rcv_buf[rcv_dir].p_max_dist
            if rcv_buf[rcv_dir].p_max_id in table_a and \
                table_a[rcv_buf[rcv_dir].p_max_id] <= own_dist:
                del table_a[rcv_buf[rcv_dir].p_max_id]
    return table_a


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
