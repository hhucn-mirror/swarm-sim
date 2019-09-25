
from lib.swarm_sim_header import *
from solution.def_distances import *
from solution.read_write import *
from solution.kalman import *

import random

cycle_no = 3


def solution(sim):
    for particle in sim.particles:

        if sim.get_actual_round() == 1:
            initialize_particle(particle)
            particle.dest_t=random.choice(sim.get_tiles_list())

        hit_a_matter = move_to_dest_step_by_step(particle, particle.dest_t)
        if hit_a_matter:
            particle.own_dist = calc_own_dist_t(hit_a_matter)
            if particle.own_dist == 1:
                print ("got a distance from a tile")


        if particle.wait:
            if sim.get_actual_round() % (cycle_no + 1) == 0:
                particle.wait = False
            else:
                #particle.delete_whole_memeory()
                continue
        if sim.get_actual_round() % cycle_no == 1:
            if particle.next_dir is not False and not particle.particle_in(particle.next_dir)\
                    and not particle.tile_in(particle.next_dir):
                particle.prev_dir = get_the_invert(particle.next_dir)
                particle.move_to(particle.next_dir)
                print ("dist list bevore moving", str(particle.nh_dist_list)[1:-1] )
                print("\n P", particle.number, " coates to", dir_to_str(particle.next_dir))
                reset_attributes(particle)
            elif move_to_dest_step_by_step(particle, particle.dest_t):
                reset_attributes(particle)

        elif sim.get_actual_round() % cycle_no == 2:
            read_data(particle)
            particle.nh_dist_list = def_distances(particle)

            particle.rcv_buf.clear()

        elif sim.get_actual_round() % cycle_no == 0:
            particle.next_dir = coating_alg(particle)
            if particle.next_dir is False:
                if particle.number is not particle.p_max.id and particle.p_max.id is not None:
                    particle.p_max_table.update({particle.p_max.id: particle.p_max.dist})
                    if send_data(particle):
                        continue

            send_own_distance(particle)


            #     #reset_attributes(particle)
                #particle.wait = True
            #     #data_clearing(particle)
            # # else:
            # #     move_to_dest_step_by_step(particle, particle.dest_t)
            # #
