from copy import deepcopy
from lib.swarm_sim_header import *
from solution import solution_header


def read_and_clear(memory):
    """
    Reads all received messages from memory and clears it
    :param memory: a particles memory
    :return: a dictionary with all messages in the memory
    """
    if debug and debug_read:
        print("memory: ", ["direction: " + direction_number_to_string(memkey) + " | " + str(mem) for memkey, mem in memory.items()])
    if memory:
        rcv_buf = deepcopy(memory)
        memory.clear()
        return rcv_buf
    return {}


def send_own_distance(particle, targets):
    """
    Sends a message in all target directions containing only the particles own_dist
    :param particle: the sender particles
    :param targets: all directions the message should be send to
    :return: none
    """
    dist_package = solution_header.OwnDistance(particle.own_dist, particle.number)
    for target_direction in targets:
        target_particle = particle.get_particle_in(target_direction)
        if debug and debug_write:
            print("P", particle.number, "sends own distance package", dist_package.particle_distance,
                  " to", target_particle.number, " in direction", direction_number_to_string(target_direction))
        # invert the direction so the receiver particle knows from where direction it got the package
        particle.write_to_with(target_particle, key=get_the_invert(target_direction), data=deepcopy(dist_package))
        # if particle.nh_list[target_direction].dist > particle.own_dist:
        #     send_distance_of_free_locations(particle, target_direction)


def send_p_max(particle, targets):
    """
        Sends a message in all target directions containing the particles own_dist and p_max
        :param particle: the sender particles
        :param targets: all directions the message should be send to
        :return: none
        """
    dist_package = solution_header.PMax(particle.own_dist, particle.number, particle.p_max, {})
    for target_direction in targets:
        target_particle = particle.get_particle_in(target_direction)
        if debug and debug_write:
            print("P", particle.number, "sends Pmax package", dist_package.p_max_dist, " to", target_particle.number,
                  " in direction", direction_number_to_string(target_direction))
        particle.write_to_with(target_particle, key=get_the_invert(target_direction), data=deepcopy(dist_package))
        # if particle.nh_list[target_direction].dist > particle.own_dist:
        #     send_distance_of_free_locations(particle, target_direction)


def send_dummy_messages(particle, targets):
    """
    Sends a message in all target directions containing only the particles own_dist
    :param particle: the sender particles
    :param targets: all directions the message should be send to
    :return: none
    """
    dist_package = solution_header.OwnDistance(math.inf, particle.number)
    for target_direction in targets:
        target_particle = particle.get_particle_in(target_direction)
        if debug and debug_write:
            print("P", particle.number, "sends own distance package", dist_package.particle_distance,
                  " to", target_particle.number, " in direction", direction_number_to_string(target_direction))
        # invert the direction so the receiver particle knows from where direction it got the package
        particle.write_to_with(target_particle, key=get_the_invert(target_direction), data=deepcopy(dist_package))
        # if particle.nh_list[target_direction].dist > particle.own_dist:
        #     send_distance_of_free_locations(particle, target_direction)


def send_distance_of_free_locations(particle, target_direction):
    """
    Sends the distance of shared free locations to a target particle
    :param particle: the sender particle
    :param target_direction: the direction of the target
    :return: none
    """
    target_particle = particle.get_particle_in(target_direction)
    for free_location_direction in [direction_in_range(target_direction - 1),
                                    direction_in_range(target_direction + 1)]:
        if particle.nh_list[free_location_direction].type == "fl":
            free_location_package = solution_header.OwnDistance(particle.nh_list[free_location_direction].dist,
                                                                None)
            particle.write_to_with(target_particle, key=get_the_invert(free_location_direction),
                                   data=deepcopy(free_location_package))


def find_neighbor_particles(particle):
    """
    Find all directions containing particles
    :param particle: the particle whose neighborhood ist checked
    :return: all directions containing particles
    """
    directions_with_particles = []
    for direction in direction_list:
        if particle.particle_in(direction):
            directions_with_particles.append(direction)
    return directions_with_particles


def divide_neighbors(nh_list, neighbor_directions, own_distance):
    p_max_targets = []
    own_distance_targets = []
    for direction in neighbor_directions:
        if nh_list[direction].dist > own_distance:
            own_distance_targets.append(direction)
        else:
            p_max_targets.append(direction)
    return own_distance_targets, p_max_targets


def send_pmax_to_neighbors(particle):
    """
    Sends information to all neighbors based on the particles own judgement
    :param particle: the sender particle
    :return: none
    """
    if particle.own_dist != math.inf:
        p_max_targets = find_neighbor_particles(particle)
        send_p_max(particle, p_max_targets)
        send_own_distance(particle, own_distance_targets)


def send_own_dist_to_neighbors(particle):
    """
    Only sends own_dist info and never sends p_max
    :param particle: the sender particle
    :return: none
    """
    if particle.own_dist != math.inf:
        directions_with_particles = find_neighbor_particles(particle)
        own_distance_targets, dummy_message_targets = divide_neighbors(particle.nh_list,
                                                   directions_with_particles,
                                                   particle.own_dist)
        send_own_distance(particle, own_distance_targets)
        if particle.waiting_rounds > 15:
            send_dummy_messages(particle, dummy_message_targets)
            particle.waiting_rounds = 0
        else:
            particle.waiting_rounds += 1
