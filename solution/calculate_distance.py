
from lib.std_lib import *
from solution.def_distances import def_distances
from solution.read_write import *
import random


def initialize_particle(particle):

    setattr(particle, "own_dist", 10000)
    #nh: neighborhood
    setattr(particle, "nh_dict", {})
    setattr(particle, "rcv_buf", {})
    setattr(particle, "prev_dir", None)

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


cycle_no = 3


def solution(sim):
    for particle in sim.particles:
        if sim.get_actual_round() == 1:
            initialize_particle(particle)
            particle.dest_t=random.choice(sim.get_tiles_list())
            #move_to_dest_in_one_rnd(particle, particle.tile)
        move_to_dest_step_by_step(particle, particle.dest_t)

        if sim.get_actual_round() % cycle_no == 1:
            reset_attributes(particle)
            read_data(particle)
            def_distances(particle)
            particle.rcv_buf.clear()
        elif sim.get_actual_round() % cycle_no == 2:
            send_data(particle)

        # elif sim.get_actual_round() % cycle_no == 0:
        #     coating_dir=coating(particle)
        #     if coating_dir is not False:
        #         particle.prev_dir = get_the_invert(coating_dir)
        #         particle.move_to(coating_dir)
        #         data_clearing(particle)
        #     else:
        #         move_to_dest_step_by_step(particle, particle.dest_t)


def coating(particle):
    if len(particle.t_dir_list) > 3:
        # Optimization movementen between tiles
        if len(particle.t_dir_list) == 4:
            return move_between_tiles(particle)
    else:
        if particle.fl_dir_list is not None:
           return move_to_fl_dir(particle)
    return False


def move_between_tiles(particle):
    for dir in particle.fl_dir_list:
        if particle.nh_dict[dir].type == "p" and particle.nh_dict[get_the_invert(dir)].type == "fl" \
        and get_the_invert(dir) != particle.prev_dir :
            return get_the_invert(dir)
        elif particle.nh_dict[dir].type == "fl" and particle.nh_dict[get_the_invert(dir + 3)].type == "fl" \
        and dir != particle.prev_dir and not particle.particle_in(dir) and not particle.tile_in(dir):
            return dir
        elif not particle.particle_in(get_the_invert(dir)) and not particle.tile_in(get_the_invert(dir)) \
        and not particle.tile_in(dir):
            return get_the_invert(dir)
    return False


def move_to_fl_dir(particle):
    if particle.gl_p_max_dir != -1 :
        for fl_dir in particle.fl_dir_list:
            if particle.gl_p_max_dist > particle.nh_dict[fl_dir].dist and \
                    particle.particle_in (fl_dir) is False:
                    return fl_dir

    return False


def data_clearing(particle):
    particle.gl_fl_min_dir = None
    particle.gl_fl_min_dist = 10000

    particle.loc_p_max_dir = None
    particle.gl_p_max_dir = None
    particle.gl_p_max_dist = -1
    particle.loc_p_max_dist = -1

    particle.wait = True