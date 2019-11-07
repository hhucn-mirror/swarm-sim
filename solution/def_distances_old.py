from lib.swarm_sim_header import *
import math

from solution.solution_header import Neighbor


class Neighbors:
    def __init__(self, type, dist):
        self.type = type
        self.dist = dist

    def __str__(self):
        return " " + str(self.type)  + " " + str(self.dist)


def scan_nh(particle):
    for dir in direction_list:
        if particle.particle_in(dir):
            particle.nh_dict[dir] = Neighbor("p", math.inf)
            particle.p_dir_list.append(dir)
        elif particle.tile_in(dir):
            particle.nh_dict[dir] = Neighbor("t", 0)
            particle.t_dir_list.append(dir)
            particle.dest_t = particle.get_tile_in(dir)
        else:
            particle.nh_dict[dir] = Neighbor("fl", math.inf)
            particle.fl_dir_list.append(dir)
    return True


def def_distances(particle):
    if debug:
        print("\n***************************************************************")
        print(" Before P", particle.number, "own distance", particle.own_dist, "coords", particle.coords)

    if scan_nh(particle) and def_own_dist(particle):
        if debug :
            print("Direction | Type | Distance")
            for dir in particle.nh_dict:
                print(direction_number_to_string(dir), "|", particle.nh_dict[dir].type, "|", particle.nh_dict[dir].dist)

        def_nh_dist(particle)

    def_min_dist_fl(particle)
    def_max_dist_p(particle)
    if debug:
        print("\n After P", particle.number, "own distance", particle.own_dist)
        print("Direction | Type | Distance")
        for dir in particle.nh_dict:
            print(direction_number_to_string(dir),"|",particle.nh_dict[dir].type, "|", particle.nh_dict[dir].dist )
        print ("local fl_min_dist", particle.loc_fl_min_dist)
        print("local fl_min_dir:")
        for dir in particle.loc_fl_min_dir:
            print (direction_number_to_string(dir))
        print ("global fl_min_dist", particle.gl_fl_min_dist, " global fl_min_dir", direction_number_to_string(particle.gl_fl_min_dir))
        print ("local p_max_dist", particle.loc_p_max_dist, " local p_max_dir", direction_number_to_string(particle.loc_p_max_dir))
        print ("global p_max_dist", particle.gl_p_max_dist, "global p_max_dir", direction_number_to_string(particle.gl_p_max_dir))


def def_own_dist(particle):
    if particle.t_dir_list:
        particle.own_dist = 1
        particle.gl_p_max_dist = 1
        return True
    else:
        for dir in particle.rcv_buf:
            if particle.rcv_buf[dir].own_dist != math.inf:
                particle.nh_dict[dir].dist = particle.rcv_buf[dir].own_dist
                if particle.rcv_buf[dir].own_dist + 1 < particle.own_dist:
                    particle.own_dist = particle.rcv_buf[dir].own_dist + 1
                    particle.gl_p_max_dist = particle.own_dist
                    particle.gl_p_max_id = particle.number
        return True
    return False


def def_nh_dist(particle):
    for dir in particle.nh_dict:
        if particle.nh_dict[dir].dist == math.inf:
            if particle.own_dist != math.inf or particle.nh_dict[direction_in_range(dir + 1)].dist != math.inf or \
                 particle.nh_dict[direction_in_range(dir - 1)].dist != math.inf:
                particle.nh_dict[dir].dist = 1 + min(particle.own_dist,
                                                     particle.nh_dict[direction_in_range(dir + 1)].dist,
                                                     particle.nh_dict[direction_in_range(dir - 1)].dist)
            else:
                particle.nh_dict[dir].dist = math.inf


def def_min_dist_fl(particle):
    for dir in particle.fl_dir_list:
        loc_min_fl(dir, particle)
    for dir in particle.rcv_buf:
        gl_min_fl(dir, particle)


def loc_min_fl(dir, particle,):
    if particle.nh_dict[dir].dist == particle.loc_fl_min_dist and len(particle.loc_fl_min_dir) > 0:
        particle.loc_fl_min_dir.append(dir)

    elif particle.nh_dict[dir].dist <= particle.own_dist:
        particle.loc_fl_min_dist= particle.gl_fl_min_dist = particle.nh_dict[dir].dist
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
    if particle.nh_dict[dir].dist > particle.gl_p_max_dist:
        particle.loc_p_max_dist = particle.gl_p_max_dist = particle.nh_dict[dir].dist
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
