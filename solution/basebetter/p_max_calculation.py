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

    own_p_max(particle.own_dist, particle.p_max, particle.number, particle.nh_list)
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
        higher_neighbors = 0
        for direction in direction_list:
            neighbor = nh_list[direction]
            if neighbor.type == "p" and p_max.dist < neighbor.dist:
                higher_neighbors += 1
        if higher_neighbors > 2:
            p_max.reset()
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
                particle.p_max.ids = {particle.number}
    return False
