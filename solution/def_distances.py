from solution.std_lib import *
import math

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

    particle.own_dist = calc_own_dist(nh_list)

    if particle.own_dist != math.inf:
        for dir in direction:
            particle.nh_dist_list[dir] = calc_nh_dist(dir, nh_list, particle.own_dist)
            #if particle is beside a tile then this tile is the new target
            if nh_list[dir].type == "t":
                particle.dest_t == particle.get_tile_in(dir)
        print("Before P MAX:")
        print("id | dist | dir | hop")
        print(particle.p_max)

        find_p_max(particle.p_max, particle.number, particle.own_dist, particle.rcv_buf)
        print ("P MAX:")
        print("id | dist | dir | hop")
        print(particle.p_max)
       # print(str(particle.p_max.id) +"|"+ str(particle.p_max.dist) +"|"+  str(particle.p_max.dir) +"|"+ str(particle.p_max.hop))
    #particle.fl_min = set_min_fl(nh_list, particle.rcv_buf)
        #def_min_dist_fl(particle)
        #def_max_dist_p(particle)
    if debug:
        print("\n After P", particle.number, "own distance", particle.own_dist)
        print("Direction | Distance")
        for dir in direction:
            print(dir_to_str(dir),"|", particle.nh_dist_list[dir])


def find_p_max(p_max, id, own_dist, rcv_buf ):
    p_max.id = id
    p_max.dist = own_dist
    p_max.dir = None
    p_max.hop = 0
    for rcv_dir in rcv_buf:
        if rcv_buf[rcv_dir].p_max_dist > p_max.dist:
            p_max.id = rcv_buf[rcv_dir].p_max_id
            p_max.dist = rcv_buf[rcv_dir].p_max_dist
            p_max.dir = rcv_dir
            p_max.hop = rcv_buf[rcv_dir].p_max_hop + 1
        elif rcv_buf[rcv_dir].p_max_dist == p_max.dist and (rcv_buf[rcv_dir].p_max_hop + 1) < p_max.hop:
            p_max.id = rcv_buf[rcv_dir].p_max_id
            p_max.dir = rcv_dir
            p_max.hop = rcv_buf[rcv_dir].p_max_hop + 1

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
                return min(nh_list[min_dir].dist, own_dist)
        return 1 + min(own_dist,
                       nh_list[dir_in_range(dir + 1)].dist,
                       nh_list[dir_in_range(dir - 1)].dist)

    return nh_list[dir].dist


def set_min_fl(nh_list, rcv_buf):
    fl_dist_list= list()
    for dir in nh_list:
        if nh_list[dir].type == "fl":
            fl_dist_list.appedn(nh_list[dir].dist)




def def_min_dist_fl(particle):
    for dir in particle.fl_dir_list:
        loc_min_fl(dir, particle)
    for dir in particle.rcv_buf:
        gl_min_fl(dir, particle)


def loc_min_fl(dir, particle,):
    if nh_list[dir].dist == particle.loc_fl_min_dist and len(particle.loc_fl_min_dir) > 0:
        particle.loc_fl_min_dir.append(dir)

    elif nh_list[dir].dist <= particle.own_dist:
        particle.loc_fl_min_dist= particle.gl_fl_min_dist = nh_list[dir].dist
        particle.loc_fl_min_dir.clear()
        particle.loc_fl_min_dir.append(dir)
        particle.gl_fl_min_dir = dir
        particle.gl_fl_min_hop = 1


def gl_min_fl(dir, particle):
    if particle.rcv_buf[dir].fl_min_dist < particle.gl_fl_min_dist:
        particle.gl_fl_min_dist = particle.rcv_buf[dir].fl_min_dist
        particle.gl_fl_min_dir = dir
        particle.gl_fl_min_hop = particle.rcv_buf[dir].fl_min_hop + 1
    elif particle.rcv_buf[dir].fl_min_dist == particle.gl_fl_min_dist \
            and particle.rcv_buf[dir].fl_min_hop + 1 < particle.gl_fl_min_hop:
        particle.gl_fl_min_dir = dir
        particle.gl_fl_min_hop = particle.rcv_buf[dir].fl_min_hop + 1


def def_max_dist_p(particle):
    for dir in particle.p_dir_list:
        loc_max_p(dir, particle)
    for dir in particle.rcv_buf:
        gl_p_max(dir, particle)

def loc_max_p(dir, particle):
    if nh_list[dir].dist > particle.gl_p_max_dist:
        particle.loc_p_max_dist = particle.gl_p_max_dist = nh_list[dir].dist
        particle.loc_p_max_dir = particle.gl_p_max_dir = dir
        particle.gl_p_max_hop = 1
        particle.gl_p_max_id = particle.get_particle_in(dir).number

def gl_p_max(dir, particle):
    if particle.rcv_buf[dir].p_max_dist != math.inf and particle.gl_p_max_dist != math.inf:
        if particle.rcv_buf[dir].p_max_dist > particle.gl_p_max_dist:
            particle.gl_p_max_dist = particle.rcv_buf[dir].p_max_dist
            particle.gl_p_max_dir = dir
            particle.gl_p_max_hop = particle.rcv_buf[dir].p_max_hop + 1
            particle.gl_p_max_id = particle.rcv_buf[dir].p_max_id
        elif particle.rcv_buf[dir].p_max_dist == particle.gl_p_max_dist \
                and  particle.rcv_buf[dir].p_max_hop + 1 < particle.gl_p_max_hop :
            particle.gl_p_max_dir = dir
            particle.gl_p_max_hop = particle.rcv_buf[dir].p_max_hop + 1
            particle.gl_p_max_id = particle.rcv_buf[dir].p_max_id
