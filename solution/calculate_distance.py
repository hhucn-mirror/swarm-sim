
black = 1
gray = 2
red = 3
green = 4
blue = 5
yellow = 6
orange = 7
cyan = 8
violett = 9

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5

direction = [NE, E, SE, SW, W, NW]

from copy import deepcopy
from solution import sp_to_tile
import random

def dir_to_str(dir):
    if dir == 0:
        return "NO"
    elif dir == 1:
        return "O"
    elif dir == 2:
        return "SO"
    elif dir == 3:
        return "SW"
    elif dir == 4:
        return "W"
    elif dir == 5:
        return "NW"
    elif dir == -1:
        return "Error"


def invert_dir(dir):
    if dir >= 3:
        return dir - 3
    else:
        return dir + 3

def dir_in_range(dir):
    if dir > 5:
        return dir - 6
    elif dir < 0:
        return dir + 6
    return dir


class neighbors:
    def __init__(self, type, dist):
        self.type = type
        self.dist = dist

    def __str__(self):
        return " " + str(self.type)  + " " + str(self.dist)
def scan_nh(particle):
    for dir in direction:
        if particle.particle_in(dir):
            particle.NH_dict[dir] = neighbors("p", -1)
            particle.p_dir.append(dir)
        elif particle.tile_in(dir):
            particle.NH_dict[dir] = neighbors("t", 0)
            particle.t_dir.append(dir)
        else:
            particle.NH_dict[dir] = neighbors("fl", 10000)
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
                particle.NH_dict[dir_in_range(particle.t_dir[0] - 1 )].dist = 1
                particle.NH_dict[dir_in_range(particle.t_dir[0] + 1 )].dist = 1
                if particle.NH_dict[dir_in_range(particle.t_dir[0] + 3)].type == "t":
                    particle.NH_dict[dir_in_range(particle.t_dir[0] + 2)].dist = 1
                    particle.NH_dict[dir_in_range(particle.t_dir[0] - 2)].dist = 1
                elif particle.NH_dict[dir_in_range(particle.t_dir[0] + 2)].type == "t":
                    particle.NH_dict[dir_in_range(particle.t_dir[0] + 3)].dist = 1
                    particle.NH_dict[dir_in_range(particle.t_dir[0] - 2)].dist = 2
                else:
                    particle.NH_dict[dir_in_range(particle.t_dir[0] + 3)].dist = 1
                    particle.NH_dict[dir_in_range(particle.t_dir[0] + 2)].dist = 2
    elif len(particle.t_dir) == 3:
            for i in range(0,3):
                if particle.NH_dict[dir_in_range(particle.t_dir[i] + 1)].type == "t"\
                and particle.NH_dict[dir_in_range(particle.t_dir[i] - 1)].type == "t":
                    particle.NH_dict[dir_in_range(particle.t_dir[i] + 2)].dist = 1
                    particle.NH_dict[dir_in_range(particle.t_dir[i] - 2)].dist = 1
                    particle.NH_dict[dir_in_range(particle.t_dir[i] + 3)].dist = 2
                    return
            for dir in  direction:
                if dir not in particle.t_dir:
                    particle.NH_dict[dir].dist = 1
    else:
        for dir in direction:
            if dir not in particle.t_dir:
                particle.NH_dict[dir].dist = 1

def check_data_received(particle):
    if particle.read_whole_memory():
        particle.rcv_buf = deepcopy(particle.read_whole_memory())
        particle.delete_whole_memeory()
        return True
    return False

class info_package:
    def __init__(self,  own_dist):
        self.own_dist = own_dist

def data_sending(particle):
    if particle.own_dist != 10000 and particle.p_dir:
        package = info_package (particle.own_dist)
        for dir in particle.p_dir:
            neighbor_p = particle.get_particle_in(dir)
            # invert the dir so the receiver particle knows from where direction it got the package
            particle.write_to_with(neighbor_p, key=invert_dir(dir), data=deepcopy(package))

cycle_no=2
def solution(sim):

    for particle in sim.particles:
        if sim.get_actual_round() == 1:
            initialize_particle(particle)
            particle.tile=random.choice(sim.get_tiles_list())
        reset_attributes(particle)
        sp_to_tile.sp(sim, particle, particle.tile)
        scan_nh(particle)
        if sim.get_actual_round() % cycle_no == 1:
            define_own_dist(particle)
            define_nh_dist(particle)
        if sim.get_actual_round() % cycle_no == 0:
            data_sending(particle)


def define_nh_dist(particle):
    if particle.own_dist != 10000:
        if particle.t_dir:
            define_dist_with_t(particle)
        if particle.p_dir:
            for dir in particle.NH_dict:
                if particle.NH_dict[dir].type == "fl":
                    if particle.NH_dict[dir_in_range(dir + 1)].type == "fl" \
                            and particle.NH_dict[dir_in_range(dir - 1)].type == "fl":
                        particle.NH_dict[dir].dist = particle.own_dist + 1
                    else:
                        particle.NH_dict[dir].dist = particle.own_dist
                if particle.NH_dict[dir].type == "p" and dir in particle.rcv_buf:
                    particle.NH_dict[dir].dist = particle.rcv_buf[dir].own_dist

        print("Particle No", particle.number, "own distance", particle.own_dist, "NH Table:")
        print("Direction|Type|Distance")
        for dir in particle.NH_dict:
            print(dir_to_str(dir), particle.NH_dict[dir])


def define_own_dist(particle):
    if particle.t_dir:
        particle.own_dist = 1
    if particle.p_dir:
        if check_data_received(particle):
            if particle.own_dist == 10000:
                particle.own_dist = particle.rcv_buf[min(particle.rcv_buf.keys(),
                                                         key=(lambda k: particle.rcv_buf[k].own_dist))].own_dist + 1

