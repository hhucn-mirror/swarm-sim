from lib.swarm_sim_header import *
import math


class TypeInfo:
    def __init__(self):
        self.id = 0
        self.dist = -math.inf
        self.dir = 0
        self.black_list = []
    def __str__(self):
        return "id: "+ str(self.id)+"|"+"dist: "+str(self.dist)+"|"+"dir: "+ str(self.dir) \
               + "|" + "Blacklist: " + str(self.black_list)[1:-1]

    def __eq__(self, id, dist, dir, hop):
        self.id = id
        self.dist = dist
        self.dir = dir
        self.black_list = []

    def reset(self):
        self.id = 0
        self.dist = -math.inf
        self.dir = 0
        self.black_list.clear()

def initialize_particle(particle):

    setattr(particle, "own_dist", math.inf)
    #nh: neighborhood
    setattr(particle, "nh_dist_list", [math.inf, math.inf, math.inf, math.inf, math.inf, math.inf,])
    setattr(particle, "rcv_buf", {})
    setattr(particle, "snd_buf", {})
    setattr(particle, "prev_dir", False)
    setattr(particle, "next_dir", False)
    setattr(particle, "first_send", True)
    setattr(particle, "p_max_table", {})

    # t: tile
    setattr(particle, "dest_t", None)

    # fl: free location
    # setattr(particle, "fl_min", TypeInfo())

    # p: particle
    setattr(particle, "p_max", TypeInfo())

    setattr(particle, "wait", False)


def reset_attributes(particle):
    particle.own_dist = math.inf
    particle.nh_dist_list.clear()
    particle.nh_dist_list = [math.inf, math.inf, math.inf, math.inf, math.inf, math.inf, ]
    particle.p_max.reset()
    particle.next_dir = False


def coating_alg(particle):
    #opt_coating(particle)
    if particle.nh_dist_list is not None:
        return  move_to_fl_dir(particle)
    return False


def move_to_fl_dir(particle):
    #Check if particle has a global p_max and it is not equal to its own distance
    if particle.p_max.dist > particle.own_dist:
        #check if the global free location is smaller than the p_max_dist
        for dir in direction_list:
            if particle.nh_dist_list[dir] < particle.p_max.dist and not particle.particle_in(dir) and \
                    not particle.tile_in(dir) and particle.prev_dir != dir:
                return dir
    return False
