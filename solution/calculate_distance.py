from copy import deepcopy
from lib.std_lib import *
import random

class Neighbors:
    def __init__(self, type, dist):
        self.type = type
        self.dist = dist

    def __str__(self):
        return " " + str(self.type)  + " " + str(self.dist)
def scan_nh(particle):
    for dir in direction:
        if particle.particle_in(dir):
            particle.NH_dict[dir] = Neighbors("p", -1)
            particle.p_dir.append(dir)
        elif particle.tile_in(dir):
            particle.NH_dict[dir] = Neighbors("t", 0)
            particle.t_dir.append(dir)
        else:
            particle.NH_dict[dir] = Neighbors("fl", 10000)
            particle.fl_cnt += 1

def initialize_particle(particle):
    setattr(particle, "own_dist", 10000)
    setattr(particle, "NH_dict", {})
    setattr(particle, "fl_cnt", 0)
    setattr(particle, "p_dir", [])
    setattr(particle, "t_dir", [])
    setattr(particle, "rcv_buf", {})
    setattr(particle, "tile", None)

def reset_attributes(particle):
    particle.NH_dict.clear()
    particle.fl_cnt = 0
    particle.p_dir.clear()
    particle.t_dir.clear()
    particle.rcv_buf.clear()

def define_dist_with_t(particle):
    if len(particle.t_dir) == 1:
        particle.NH_dict[dir_in_range(particle.t_dir[0] + 1)].dist = 1
        particle.NH_dict[dir_in_range(particle.t_dir[0] - 1)].dist = 1
        particle.NH_dict[dir_in_range(particle.t_dir[0] + 2)].dist = 2
        particle.NH_dict[dir_in_range(particle.t_dir[0] - 2)].dist = 2
        particle.NH_dict[dir_in_range(particle.t_dir[0] + 3)].dist = 2
    elif len(particle.t_dir) == 2:
        if particle.NH_dict[dir_in_range(particle.t_dir[0] + 1)].type != "t"\
        and particle.NH_dict[dir_in_range(particle.t_dir[0] - 1)].type != "t":
            define_dist_for_2_t(particle)
    elif len(particle.t_dir) == 3:
        for i in range(0,3):
            if particle.NH_dict[dir_in_range(particle.t_dir[i] + 1)].type == "t"\
            and particle.NH_dict[dir_in_range(particle.t_dir[i] - 1)].type == "t":
                particle.NH_dict[dir_in_range(particle.t_dir[i] + 2)].dist = 1
                particle.NH_dict[dir_in_range(particle.t_dir[i] - 2)].dist = 1
                particle.NH_dict[dir_in_range(particle.t_dir[i] + 3)].dist = 2
                return
        for dir in direction:
            if dir not in particle.t_dir:
                particle.NH_dict[dir].dist = 1
    else:
        for dir in direction:
            if dir not in particle.t_dir:
                particle.NH_dict[dir].dist = 1


def define_dist_for_2_t(particle):
    particle.NH_dict[dir_in_range(particle.t_dir[0] - 1)].dist = 1
    particle.NH_dict[dir_in_range(particle.t_dir[0] + 1)].dist = 1
    if particle.NH_dict[dir_in_range(particle.t_dir[0] + 2)].type == "t":
        particle.NH_dict[dir_in_range(particle.t_dir[0] + 3)].dist = 1
        particle.NH_dict[dir_in_range(particle.t_dir[0] - 2)].dist = 2
    elif particle.NH_dict[dir_in_range(particle.t_dir[0] + 3)].type == "t":
        particle.NH_dict[dir_in_range(particle.t_dir[0] + 2)].dist = 1
        particle.NH_dict[dir_in_range(particle.t_dir[0] - 2)].dist = 1
    else:
        particle.NH_dict[dir_in_range(particle.t_dir[0] + 3)].dist = 1
        particle.NH_dict[dir_in_range(particle.t_dir[0] + 2)].dist = 2


def check_data_received(particle):
    if particle.read_whole_memory():
        particle.rcv_buf = deepcopy(particle.read_whole_memory())
        particle.delete_whole_memeory()
        return True
    return False

class InfoPackage:
    def __init__(self,  own_dist):
        self.own_dist = own_dist

def data_sending(particle):
    if particle.own_dist != 10000 and particle.p_dir:
        package = InfoPackage (particle.own_dist)
        for dir in particle.p_dir:
            neighbor_p = particle.get_particle_in(dir)
            # invert the dir so the receiver particle knows from where direction it got the package
            particle.write_to_with(neighbor_p, key=get_the_invert(dir), data=deepcopy(package))

cycle_no=2
def solution(sim):
    for particle in sim.particles:
        if sim.get_actual_round() == 1:
            initialize_particle(particle)
            particle.tile=random.choice(sim.get_tiles_list())
        reset_attributes(particle)
        move_to_dest_in_one_rnd(particle, particle.tile)
        #move_to_dest_step_by_step(particle, particle.tile)

        scan_nh(particle)
        if sim.get_actual_round() % cycle_no == 1:
            define_own_dist(particle)
            if particle.own_dist != 10000:
                define_nh_dist(particle)
        if sim.get_actual_round() % cycle_no == 0:
            data_sending(particle)

def define_nh_dist(particle):
        if particle.t_dir:
            define_dist_with_t(particle)
        if particle.p_dir:
            define_dist_with_p(particle)
        print("Particle No", particle.number, "own distance", particle.own_dist, "NH Table:")
        print("Direction|Type|Distance")
        for dir in particle.NH_dict:
            print(dir_to_str(dir), particle.NH_dict[dir])


def define_dist_with_p(particle):
    for dir in particle.NH_dict:
        if particle.NH_dict[dir].type == "fl":
            check_beside_fl(dir, particle)
        if particle.NH_dict[dir].type == "p" and dir in particle.rcv_buf:
            particle.NH_dict[dir].dist = particle.rcv_buf[dir].own_dist


def check_beside_fl(dir, particle):
    if particle.NH_dict[dir_in_range(dir + 1)].type == "fl" \
            and particle.NH_dict[dir_in_range(dir - 1)].type == "fl":
        particle.NH_dict[dir].dist = particle.own_dist + 1
    else:
        particle.NH_dict[dir].dist = particle.own_dist


def define_own_dist(particle):
    if particle.t_dir:
        particle.own_dist = 1
    if particle.p_dir and check_data_received(particle) and particle.own_dist == 10000:
        particle.own_dist = particle.rcv_buf[min(particle.rcv_buf.keys(),
                                             key=(lambda k: particle.rcv_buf[k].own_dist))].own_dist + 1

