from lib import config
import importlib
import random
from lib.swarm_sim_header import *


coating_folder = config.ConfigData().coating_algorithm
distance_calc_mod = importlib.import_module("solution." + coating_folder + ".distance_calculation", "solution." + coating_folder)
read_write_mod = importlib.import_module("solution." + coating_folder + ".read_write", "solution." + coating_folder)
p_max_calc_mod = importlib.import_module("solution." + coating_folder + ".p_max_calculation", "solution." + coating_folder)
coating_mod = importlib.import_module("solution." + coating_folder + ".coating_alg", "solution." + coating_folder)

cycle_no = 3


def solution(sim):
    for particle in sim.particles:
        if sim.get_actual_round() == 1:
            coating_mod.initialize_particle(particle)
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
            move_cycle(particle)

        elif sim.get_actual_round() % cycle_no == 2:
            read_cycle(particle)

        elif sim.get_actual_round() % cycle_no == 0:
            write_cycle(particle)


def write_cycle(particle):
    """
    lets the current particle send messages to its neighbors.
    :param particle: the particle whose turn it is
    :return: none
    """
    particle.next_direction = coating_mod.coating_alg(particle)
    if len(particle.p_max.ids) > 0 and particle.p_max.dist > 0 and particle.next_direction is False:
        # particle.p_max_table.update({particle.p_max.id: particle.p_max.dist})
        read_write_mod.send_pmax_to_neighbors(particle)
    else:
        read_write_mod.send_own_dist_to_neighbors(particle)


def read_cycle(particle):
    """
    Lets the current particle read messages from its neighbors and calculate distances for each neighbor location.
    :param particle: the particle whose turn it is
    :return:  none
    """
    if debug and debug_read:
        print("reading memory of particle", particle.number)
    particle.rcv_buf = read_write_mod.read_and_clear(particle.read_whole_memory())
    particle.nh_list = distance_calc_mod.calculate_distances(particle)
    p_max_calc_mod.find_p_max(particle)
    particle.rcv_buf.clear()


def move_cycle(particle):
    """
    Lets the current particle move.
    :param particle: the particle whose turn it is
    :return: none
    """
    if particle.next_direction is False and particle.own_dist > 1:
        if debug and debug_movement:
            print("moving closer to target tile")
        move_to_target_tile(particle)
    elif particle.next_direction is not False and not particle.particle_in(particle.next_direction) \
            and not particle.tile_in(particle.next_direction):
        move_to_next_dir(particle)
    coating_mod.reset_p_max(particle)


def move_to_next_dir(particle):
    """
    Moves the particle to the next direction calculated by the algorithm.
    :param particle: the particle whose turn it is
    :return: none
    """
    particle.prev_direction = get_the_invert(particle.next_direction)
    particle.move_to(particle.next_direction)
    if debug:
        print("dist list before moving", [str(neighbor) for neighbor in particle.nh_list])
        print("\n P", particle.number, " coates to", direction_number_to_string(particle.next_direction))
    coating_mod.reset_attributes(particle)
    coating_mod.reset_p_max(particle)


def move_to_target_tile(particle):
    """
    Moves the particle in the global direction of it's target tile.
    This method uses information from the world class.
    :param particle: the particle whose turn it is
    :return: none
    """
    hit_a_matter = move_to_dest_step_by_step(particle, particle.dest_t, particle.prev_direction)
    if hit_a_matter or hit_a_matter is None:
        # reset_attributes(particle)
        if hit_a_matter is not None:
            if particle.own_dist > distance_calc_mod.calc_own_dist_t(hit_a_matter):
                particle.own_dist = distance_calc_mod.calc_own_dist_t(hit_a_matter)
            if hit_a_matter.type == "tile" and debug:
                print("got a distance from a tile")
    else:
        coating_mod.reset_attributes(particle)
        coating_mod.reset_p_max(particle)
