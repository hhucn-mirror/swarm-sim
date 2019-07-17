
from lib.std_lib import *
from solution.def_distances import def_distances
from solution.read_write import *
import random


def initialize_particle(particle):

    setattr(particle, "own_dist", 10000)
    #nh: neighborhood
    setattr(particle, "nh_dict", {})
    setattr(particle, "rcv_buf", {})


    # t: tile
    setattr(particle, "t_dir_list", [])
    setattr(particle, "dest_t", None)

    # fl: free location
    setattr(particle, "fl_dir_list", [])
    setattr(particle, "gl_fl_min_dist", 10000)
    setattr(particle, "gl_fl_min_dir", None)
    setattr(particle, "gl_fl_min_hop", 0)
    setattr(particle, "loc_fl_min_dist", 10000)
    setattr(particle, "loc_fl_min_dir", None)

    # p: particle
    setattr(particle, "p_dir_list", [])
    setattr(particle, "gl_p_max_dist", -1)
    setattr(particle, "gl_p_max_dir", None)
    setattr(particle, "gl_p_max_hop", 0)
    setattr(particle, "loc_p_max_dist", -1)
    setattr(particle, "loc_p_max_dir", None)

def reset_attributes(particle):
    particle.nh_dict.clear()
    particle.p_dir_list.clear()
    particle.t_dir_list.clear()
    particle.fl_dir_list.clear()
    particle.rcv_buf.clear()


cycle_no = 2


def solution(sim):
    for particle in sim.particles:

        if sim.get_actual_round() == 1:
            initialize_particle(particle)
            particle.dest_t=random.choice(sim.get_tiles_list())
            #move_to_dest_in_one_rnd(particle, particle.tile)

        reset_attributes(particle)

        move_to_dest_step_by_step(particle, particle.dest_t)

        if sim.get_actual_round() % cycle_no == 1:
            read_data(particle)
            def_distances(particle)
            def_min_dist_fl(particle)
            #def_max_dist_p(particle)
            particle.rcv_buf.clear()
        if sim.get_actual_round() % cycle_no == 0:
            send_data(particle)


def def_min_dist_fl(particle):
    for dir in particle.fl_dir_list:
        if particle.nh_dict[dir].dist < particle.loc_fl_min_dist:
            particle.loc_fl_min_dist = particle.nh_dict[dir].dist
            particle.loc_fl_min_dir = dir



#def def_max_dist_p(particle)
