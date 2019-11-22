from lib.swarm_sim_header import *
import math

from solution import solution_header


def initialize_particle(particle):
    """
    Adds all instance attributes to the particle and initializes them
    :param particle: the particle to initialize
    :return: none
    """
    setattr(particle, "own_dist", math.inf)
    # nh: neighborhood
    setattr(particle, "nh_list", [solution_header.Neighbor("fl", math.inf)] * 6)
    setattr(particle, "rcv_buf", {})
    setattr(particle, "snd_buf", {})
    # setattr(particle, "prev_direction", False)
    setattr(particle, "next_direction", False)
    setattr(particle, "prev_direction", False)

    # t: tile
    setattr(particle, "dest_t", None)

    # fl: free location
    # setattr(particle, "fl_min", PMaxInfo())

    # p: particle
    setattr(particle, "p_max", solution_header.PMaxInfo())
    setattr(particle, "wait", False)


def reset_attributes(particle):
    """
    Resets particle variables that are based on the particles position
    :param particle: the particle to reset
    :return: none
    """
    if debug:
        print("resetting particle", particle.number)
    particle.own_dist = math.inf
    # particle.nh_list.clear()
    particle.nh_list = [solution_header.Neighbor("fl", math.inf)] * 6
    particle.next_direction = False
    particle.read_whole_memory().clear()


def reset_p_max(particle):
    """
    resets all pmax related particle variables
    :param particle: the particle to reset
    :return: none
    """
    particle.p_max.reset()


def coating_alg(particle):
    """
    Main coating algorithm function. checks if nh_list is not None and then calls actual calculation.
    :param particle: the particle for which the next direction should be calculated
    :return: the next direction the particle should move to
    """
    #opt_coating(particle)
    if particle.nh_list is not None:
        return find_next_free_location(particle)
    return False


def find_next_free_location(particle):
    """
    calculates the next move direction for a particle
    :param particle: the particle for which the next direction should be calculated
    :return: the next direction the particle should move to
    """
    # Check if particle has a global p_max and it is not equal to its own distance
    possible_directions = []
    # accumulate all candidates for the next movement direction in possible_directions
    for direction in reversed(direction_list):
        if not (particle.particle_in(direction) or         # check if direction is free
                particle.tile_in(direction) or
                particle.prev_direction == direction) and\
                particle.nh_list[direction].dist < particle.p_max.dist:
            possible_directions.append((direction, particle.nh_list[direction].dist))
    if len(possible_directions) > 0:
        nearest_free_location = min(possible_directions, key=lambda x: x[1])
        return nearest_free_location[0]
    return False
