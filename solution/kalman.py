from solution.std_lib import *
import math

class TypeInfo:
    def __init__(self):
        self.id = 0
        self.dist = -math.inf
        self.dir = 0
        self.hop = 0

    def __str__(self):
        return "id: "+ str(self.id)+"|"+"dist: "+str(self.dist)+"|"+"dir: "+ str(self.dir)+"|"+"hop: "+ str(self.hop)

    def __eq__(self, id, dist, dir, hop):
        self.id = id
        self.dist = dist
        self.dir = dir
        self.hop = hop



def initialize_particle(particle):

    setattr(particle, "own_dist", math.inf)
    #nh: neighborhood
    setattr(particle, "nh_dist_list", [math.inf, math.inf, math.inf, math.inf, math.inf, math.inf,])
    setattr(particle, "rcv_buf", {})
    setattr(particle, "prev_dir", None)
    setattr(particle, "next_dir", None)

    # t: tile
    setattr(particle, "dest_t", None)

    # fl: free location
    setattr(particle, "fl_min", TypeInfo())

    # p: particle
    setattr(particle, "p_max", TypeInfo())

    setattr(particle, "wait", False)


def reset_attributes(particle):
    particle.next_dir = None
    data_clearing(particle)


def data_clearing(particle):
    particle.own_dist = math.inf


def coating_alg(particle):
    #opt_coating(particle)
    if particle.fl_dir_list is not None:
        return  move_to_fl_dir(particle)
    return False


def move_to_fl_dir(particle):
    #Check if particle has a global p_max and it is not equal to its own distance
    if particle.gl_p_max_dist != math.inf and particle.gl_p_max_dist != particle.own_dist:
        #check if the global free location is smaller than the p_max_dist
        if particle.gl_fl_min_dist < particle.gl_p_max_dist and particle.particle_in(particle.gl_fl_min_dir) is False\
                and particle.tile_in (particle.gl_fl_min_dir) is False:
            return particle.gl_fl_min_dir
        else:
            for fl_dir in particle.fl_dir_list:
                if particle.gl_p_max_dist > particle.nh_dict[fl_dir].dist and \
                        particle.particle_in (fl_dir) is False:
                    return fl_dir
    else:
        if particle.gl_fl_min_dist != math.inf and particle.particle_in(particle.gl_fl_min_dir) is False\
                and particle.tile_in(particle.gl_fl_min_dir) is False:
            return particle.gl_fl_min_dir
    return False
