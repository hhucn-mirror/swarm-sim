from copy import deepcopy
import math
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


def send_own_distance(particle):
    if particle.own_dist != math.inf:
        dist_package = message.OwnDist(particle.own_dist, particle.number)
        for dir in direction_list:
            neighbor_p = particle.get_particle_in(dir)
            if neighbor_p:
                if debug and debug_write:
                    print("P", particle.number, "sends own distance package", dist_package.own_dist,
                          " to", neighbor_p.number, " in dir", direction_number_to_string(dir))
                # invert the dir so the receiver particle knows from where direction it got the package
                particle.write_to_with(neighbor_p, key=get_the_invert(dir), data=deepcopy(dist_package))
                for free_location_dir in [direction_in_range(dir - 1), direction_in_range(dir + 1)]:
                    if particle.nh_dist_list[free_location_dir].type == "fl":
                        free_location_package = message.OwnDist(particle.nh_dist_list[free_location_dir].dist, None)
                        particle.write_to_with(neighbor_p, key=get_the_invert(free_location_dir), data=deepcopy(free_location_package))
        return True
    return False


def send_p_max(particle):
    if particle.own_dist != math.inf:
        send_p_max_counter = len(particle.p_max.dir) if len(particle.p_max.dir) > 0 else 1
        direction_rotation = 0
        if len(particle.p_max.dir) == 0:
            direction_rotation = find_lowest_distance_neighbor_direction(particle.nh_dist_list, particle.own_dist)
        rotated_direction_list = rotate_list(direction_list, direction_rotation)
        for dir in rotated_direction_list:
            dist_package = message.PMax(particle.own_dist, particle.number, particle.p_max, particle.p_max_table)
            neighbor_p = particle.get_particle_in(dir)
            if neighbor_p:
                if debug and debug_write:
                    print("P", particle.number, "sends Pmax package", dist_package.p_max_dist, " to", neighbor_p.number,
                          " in dir", direction_number_to_string(dir))

                if (particle.own_dist == particle.nh_dist_list[dir].dist and send_p_max_counter == 0) or \
                        dir in particle.p_max.dir or particle.own_dist < particle.nh_dist_list[dir].dist:
                    dist_package = message.OwnDist(particle.own_dist, particle.number)
                elif particle.own_dist == particle.nh_dist_list[dir].dist:
                    send_p_max_counter -= 1
                # invert the dir so the receiver particle knows from where direction it got the package
                particle.write_to_with(neighbor_p, key=get_the_invert(dir), data=deepcopy(dist_package))
        return True
    return False



def send_to(rcver, dir, snd_buf, sender):
    if rcver and snd_buf:
        if debug and debug_write:
            print("sends ", snd_buf,
                  "to P", rcver.number, " in dir", direction_number_to_string(dir))
        # invert the dir so the receiver particle knows from where direction it got the package
        sender.write_to_with(rcver, key=get_the_invert(dir), data=deepcopy(snd_buf))
        return True
    return False
