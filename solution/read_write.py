from copy import deepcopy
from lib.swarm_sim_header import *
import solution.message as message


# def __init__(self, own_dist, fl_min_dist, fl_hop, p_max_id, p_max_dist, p_hop):
# self.own_dist = own_dist
# self.fl_min_dist = fl_min_dist
# self.fl_min_hop = fl_hop
# self.p_max_dist = p_max_dist
# self.p_max_hop = p_hop
# self.p_max_id = p_max_id


def read(memory):
    if debug and debug_read:
        print("memory: ", ["direction: " + direction_number_to_string(memkey) + " | " + str(mem) for memkey, mem in memory.items()])
    if memory:
        rcv_buf = deepcopy(memory)
        memory.clear()
        return rcv_buf
    return {}


def send_own_distance(particle, targets):
    dist_package = message.OwnDistance(particle.own_dist, particle.number)
    for target_direction in targets:
        target_particle = particle.get_particle_in(target_direction)
        if debug and debug_write:
            print("P", particle.number, "sends own distance package", dist_package.particle_distance,
                  " to", target_particle.number, " in direction", direction_number_to_string(target_direction))
        # invert the direction so the receiver particle knows from where direction it got the package
        particle.write_to_with(target_particle, key=get_the_invert(target_direction), data=deepcopy(dist_package))
        send_distance_of_free_locations(particle, target_direction, target_particle)


def send_p_max(particle, targets):
    dist_package = message.PMax(particle.own_dist, particle.number, particle.p_max, particle.p_max_table)
    for target_direction in targets:
        target_particle = particle.get_particle_in(target_direction)
        if debug and debug_write:
            print("P", particle.number, "sends Pmax package", dist_package.p_max_dist, " to", target_particle.number,
                  " in direction", direction_number_to_string(target_direction))
        particle.write_to_with(target_particle, key=get_the_invert(target_direction), data=deepcopy(dist_package))
        send_distance_of_free_locations(particle, target_direction, target_particle)


def send_distance_of_free_locations(particle, target_direction, target_particle):
    for free_location_direction in [direction_in_range(target_direction - 1), direction_in_range(target_direction + 1)]:
        if particle.nh_list[free_location_direction].type == "fl":
            free_location_package = message.OwnDistance(particle.nh_list[free_location_direction].dist, None)
            particle.write_to_with(target_particle, key=get_the_invert(free_location_direction),
                                   data=deepcopy(free_location_package))


def find_neighbor_particles(particle):
    directions_with_particles = []
    for direction in direction_list:
        if particle.particle_in(direction):
            directions_with_particles.append(direction)
    return directions_with_particles


def divide_neighbors(particle, directions_with_particles):
    send_p_max_counter = len(particle.p_max.directions) if len(particle.p_max.directions) > 0 else 1
    direction_rotation = 0
    if len(particle.p_max.directions) == 0:
        direction_rotation = find_lowest_distance_neighbor_direction(particle.nh_list)
    rotated_direction_list = rotate_list(direction_list, direction_rotation)
    targets_for_own_dist_package = directions_with_particles
    targets_for_pmax_package = []
    for direction in rotated_direction_list:
        if direction in directions_with_particles:
            if particle.own_dist == particle.nh_list[direction].dist and send_p_max_counter > 0 and \
                    direction not in particle.p_max.directions:
                targets_for_own_dist_package.remove(direction)
                targets_for_pmax_package.append(direction)
                send_p_max_counter -= 1
            elif particle.own_dist > particle.nh_list[direction].dist and direction not in particle.p_max.directions:
                targets_for_own_dist_package.remove(direction)
                targets_for_pmax_package.append(direction)
    for direction in particle.p_max.directions:
        if send_p_max_counter > 0:
            if direction in targets_for_own_dist_package:
                targets_for_own_dist_package.remove(direction)
                targets_for_pmax_package.append(direction)
                send_p_max_counter -= 1
    return targets_for_pmax_package, targets_for_own_dist_package


def send_pmax_to_neighbors(particle):
    if particle.own_dist != math.inf:
        directions_with_particles = find_neighbor_particles(particle)
        if particle.broadcast_pmax:
            send_p_max(particle, directions_with_particles)
            particle.broadcast_pmax = False
        else:
            pmax_targets, own_dist_targets = divide_neighbors(particle, directions_with_particles)
            send_p_max(particle, pmax_targets)
            send_own_distance(particle, own_dist_targets)


def send_own_dist_to_neighbors(particle):
    if particle.own_dist != math.inf:
        directions_with_particles = find_neighbor_particles(particle)
        send_own_distance(particle, directions_with_particles)