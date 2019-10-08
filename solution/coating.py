
from lib.swarm_sim_header import *
from solution.def_distances import *
from solution.read_write import *
from solution.kalman import *
from solution.def_p_max import *

import random

cycle_no = 3


def solution(sim):
    for particle in sim.particles:

        if sim.get_actual_round() == 1:
            initialize_particle(particle)
            particle.dest_t=random.choice(sim.get_tiles_list())



        if particle.wait:
            if sim.get_actual_round() % (cycle_no + 1) == 0:
                particle.wait = False
            else:
                #particle.delete_whole_memeory()
                continue
        if sim.get_actual_round() % (cycle_no * 10) == 1:
            particle.prev_direction = None
        if sim.get_actual_round() % cycle_no == 1:
            if particle.next_direction is False and particle.own_dist > 1:
                if debug and debug_movement:
                    print("moving closer to target tile")
                hit_a_matter = move_to_dest_step_by_step(particle, particle.dest_t, particle.prev_direction)
                if hit_a_matter or hit_a_matter is None:
                    #reset_attributes(particle)
                    if hit_a_matter is not None:
                        if particle.own_dist > calc_own_dist_t(hit_a_matter):
                            particle.own_dist = calc_own_dist_t(hit_a_matter)
                        if hit_a_matter.type == "tile" and debug:
                            print("got a distance from a tile")
                else:
                    reset_attributes(particle)
                    reset_p_max(particle)
            elif particle.next_direction is not False and not particle.particle_in(particle.next_direction)\
                    and not particle.tile_in(particle.next_direction):
                particle.prev_direction = get_the_invert(particle.next_direction)
                particle.move_to(particle.next_direction)
                if debug:
                    print("dist list bevore moving", [str(neighbor) for neighbor in particle.nh_dist_list])
                    print("\n P", particle.number, " coates to", direction_number_to_string(particle.next_direction))
                reset_attributes(particle)
                reset_p_max(particle)
            # elif move_to_dest_step_by_step(particle, particle.dest_t):
                # reset_attributes(particle)
            reset_p_max(particle)
        elif sim.get_actual_round() % cycle_no == 2:
            if debug and debug_read:
                print("reading memory of particle", particle.number)
            particle.rcv_buf = read(particle.read_whole_memory())
            particle.nh_dist_list = def_distances(particle)
            def_p_max(particle)
            particle.rcv_buf.clear()

        elif sim.get_actual_round() % cycle_no == 0:
            particle.next_direction = coating_alg(particle)
            if particle.p_max.id is not None and particle.p_max.dist > 0 and particle.next_direction is False:
                particle.p_max_table.update({particle.p_max.id: particle.p_max.dist})
                send_pmax_to_neighbors(particle)
            else:
                send_own_dist_to_neighbors(particle)


            #     #reset_attributes(particle)
                #particle.wait = True
            #     #data_clearing(particle)
            # # else:
            # #     move_to_dest_step_by_step(particle, particle.dest_t)
            # #
