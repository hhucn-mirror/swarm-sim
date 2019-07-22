
from lib.std_lib import *
from solution.def_distances import def_distances
from solution.read_write import *
from solution.kalman import coating

import random


def initialize_particle(particle):

    setattr(particle, "own_dist", 10000)
    #nh: neighborhood
    setattr(particle, "nh_dict", {})
    setattr(particle, "rcv_buf", {})
    setattr(particle, "prev_dir", None)
    setattr(particle, "next_dir", None)

    # t: tile
    setattr(particle, "t_dir_list", [])
    setattr(particle, "dest_t", None)

    # fl: free location
    setattr(particle, "fl_dir_list", [])
    setattr(particle, "gl_fl_min_dist", 10000)
    setattr(particle, "gl_fl_min_dir", None)
    setattr(particle, "gl_fl_min_hop", 0)
    setattr(particle, "loc_fl_min_dist", 10000)
    setattr(particle, "loc_fl_min_dir", [])

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
    particle.loc_fl_min_dir.clear()
    particle.loc_fl_min_dist = 10000
    particle.loc_p_max_dist = -1
    particle.loc_p_max_dir = None
    data_clearing(particle)
    particle.next_dir = None


def data_clearing(particle):
    particle.gl_fl_min_dir = None
    particle.gl_fl_min_dist = 10000
    particle.gl_fl_min_hop = 0

    particle.gl_p_max_dist = -1
    particle.gl_p_max_dir = None
    particle.gl_p_max_hop = 0

    #particle.rcv_buf.clear()
    #particle.delete_whole_memeory()
    particle.own_dist = 10000
    # if particle.own_dist != 10000:
    #     particle.own_dist = particle.own_dist - 1


cycle_no = 4


def solution(sim):
    for particle in sim.particles:
        if sim.get_actual_round() == 1:
            initialize_particle(particle)
            particle.dest_t=random.choice(sim.get_tiles_list())
            #move_to_dest_in_one_rnd(particle, particle.dest_t)
        #move_to_dest_step_by_step(particle, particle.dest_t)

        if sim.get_actual_round() % cycle_no == 1:
            reset_attributes(particle)
            read_data(particle)
            def_distances(particle)
            particle.rcv_buf.clear()
        elif sim.get_actual_round() % cycle_no == 2:
            send_data(particle)

        elif sim.get_actual_round() % cycle_no == 3:
            particle.next_dir = coating_dir=coating(particle)

        elif sim.get_actual_round() % cycle_no == 0:

            if particle.next_dir is not False and not particle.particle_in(particle.next_dir)\
                    and not particle.tile_in(particle.next_dir):
                particle.prev_dir = get_the_invert(particle.next_dir)
                particle.move_to(particle.next_dir)
                print("\n P", particle.number, " coates to", dir_to_str(particle.next_dir))

            else:
                move_to_dest_step_by_step(particle, particle.dest_t)

