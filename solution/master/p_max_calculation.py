from copy import deepcopy

from lib.swarm_sim_header import *
from solution import solution_header


def find_p_max(particle):
    """
    calculates the p_max for a particle based on all information this particle has
    :param particle: the particle for which the p_max should be calculated
    :return: none
    """
    if debug and debug_p_max_calculation:
        print("\n After P", particle.number, "own distance", particle.own_dist)
        print("Direction | Distance")
        for direction in direction_list:
            print(direction_number_to_string(direction), "|", particle.nh_list[direction])
        print("Before P MAX:")
        print("id | dist | direction")
        print(particle.p_max)

    if own_p_max(particle.own_dist, particle.p_max, particle.number, particle.nh_list):
        particle.own_p_max_lifetime += 1
        if particle.p_max.lifetime < particle.own_p_max_lifetime:
            particle.p_max.lifetime = particle.own_p_max_lifetime
    global_p_max(particle)

    if debug and debug_p_max_calculation:
        print("P MAX:")
        print("id | dist | direction")
        print(particle.p_max)

    if debug and debug_p_max_calculation:
        print("P_Max Table \n ID | Distance")
        print(particle.p_max_table)


def own_p_max(own_distance, p_max, particle_number, nh_list):
    """
    Checks if this particle has maximum distance
    :param own_distance: the distance of this particle
    :param p_max: the current p_max of this particle
    :param particle_number: the particles id
    :param nh_list: the particles neighborhood
    :return: True if this particle is at maximum distance, False otherwise
    """
    if own_distance is not math.inf:
        p_max.dist = own_distance
        p_max.ids = {particle_number}
        for direction in direction_list:
            neighbor = nh_list[direction]
            if neighbor.type == "p" and p_max.dist < neighbor.dist:
                p_max.dist = neighbor.dist
        return True
    return False


def global_p_max(particle):
    """
    Finds the greatest p_max in all messages received
    :param particle: the particle for which the p_max should be calculated
    :return: False
    """
    for rcv_direction in particle.rcv_buf:
        if isinstance(particle.rcv_buf[rcv_direction], solution_header.PMax):
            if particle.rcv_buf[rcv_direction].p_max_dist > particle.p_max.dist:
                particle.p_max.dist = particle.rcv_buf[rcv_direction].p_max_dist
                particle.p_max.ids = deepcopy(particle.rcv_buf[rcv_direction].p_max_ids)
                particle.p_max.lifetime = particle.rcv_buf[rcv_direction].p_max_lifetime
                particle.own_p_max_lifetime = 0
            elif particle.rcv_buf[rcv_direction].p_max_dist == particle.p_max.dist:
                particle.p_max.ids |= particle.rcv_buf[rcv_direction].p_max_ids
                if particle.p_max.lifetime < particle.rcv_buf[rcv_direction].p_max_lifetime:
                    particle.p_max.lifetime = particle.rcv_buf[rcv_direction].p_max_lifetime
    return False


def check_for_update(p_max, rcv_buf, particle_distance, particle_id):
    """
    Checks if the current Pmax is outdated by comparing ids of the current pmax and messages
    :param p_max: the particles current p_max
    :param rcv_buf: all messages in this particles memory
    :param particle_distance: the particles current distance
    :param particle_id: the particles id
    :return: None
    """
    for rcv_direction in rcv_buf:
        # checks if the current p_max is outdated and should be reduced
        check_p_max_messages(p_max, rcv_buf, rcv_direction)
        check_if_self_is_p_max(p_max, particle_distance, particle_id, rcv_direction)


def check_if_self_is_p_max(p_max, particle_distance, particle_id, rcv_direction):
    if particle_id in p_max.ids and particle_distance < p_max.dist:
        p_max.ids = {particle_id}
        p_max.dist = particle_distance


def check_p_max_messages(p_max, rcv_buf, rcv_direction):
    if isinstance(rcv_buf[rcv_direction], solution_header.PMax) and rcv_buf[rcv_direction].p_max_dist < p_max.dist \
            and any(id in rcv_buf[rcv_direction].p_max_ids for id in p_max.ids):
        p_max.ids = rcv_buf[rcv_direction].p_max_ids
        p_max.dist = rcv_buf[rcv_direction].p_max_dist
