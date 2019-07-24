
from solution.std_lib import *
from solution.def_distances import def_distances
from solution.read_write import *
from solution.kalman import *

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
                particle.delete_whole_memeory()
                continue

        if sim.get_actual_round() % cycle_no == 1:
            move_to_dest_step_by_step(particle, particle.dest_t)
            reset_attributes(particle)
            read_data(particle)
            def_distances(particle)
            particle.rcv_buf.clear()

        elif sim.get_actual_round() % cycle_no == 2:
            send_data(particle)

        elif sim.get_actual_round() % cycle_no == 0:
            pass
            #particle.next_dir = coating_alg(particle)

            # if particle.next_dir is not False and not particle.particle_in(particle.next_dir)\
            #         and not particle.tile_in(particle.next_dir):
            #     particle.prev_dir = get_the_invert(particle.next_dir)
            #     particle.move_to(particle.next_dir)
            #     print("\n P", particle.number, " coates to", dir_to_str(particle.next_dir))
            #     #reset_attributes(particle)
            #     particle.wait = True
            #     #data_clearing(particle)
            # # else:
            # #     move_to_dest_step_by_step(particle, particle.dest_t)
            # #
