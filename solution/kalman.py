from lib.swarm_sim_header import *
import math


def initialize_particle(particle):

    setattr(particle, "own_dist", math.inf)
    # nh: neighborhood
    setattr(particle, "nh_list", [Neighbor("fl", math.inf)] * 6)
    setattr(particle, "rcv_buf", {})
    setattr(particle, "snd_buf", {})
    setattr(particle, "prev_direction", False)
    setattr(particle, "next_direction", False)
    setattr(particle, "first_send", True)
    setattr(particle, "p_max_table", {})
    setattr(particle, "keep_distance", False)
    setattr(particle, "broadcast_pmax", False)
    setattr(particle, "stop_sending", False)

    # t: tile
    setattr(particle, "dest_t", None)

    # fl: free location
    # setattr(particle, "fl_min", PMaxInfo())

    # p: particle
    setattr(particle, "p_max", PMaxInfo())

    setattr(particle, "wait", False)


def reset_attributes(particle):
    if debug:
        print("resetting particle", particle.number)
    particle.own_dist = math.inf
    # particle.nh_list.clear()
    particle.nh_list = [Neighbor("fl", math.inf)] * 6
    particle.next_direction = False
    particle.keep_distance = False
    particle.read_whole_memory().clear()


def reset_p_max(particle):
    particle.p_max.reset()
    particle.p_max_table.clear()

def coating_alg(particle):
    #opt_coating(particle)
    if particle.nh_list is not None:
        return find_next_free_location(particle)
    return False


def find_next_free_location(particle):
    # Check if particle has a global p_max and it is not equal to its own distance
    # check if the local free location is smaller than the p_max_dist
    possible_directions = []
    # (particle.nh_list[direction].dist != particle.p_max.dist - 1 or particle.own_dist !yy= particle.nh_list[direction].dist))
    for direction in reversed(direction_list):
        if (particle.nh_list[direction].dist < particle.p_max.dist or particle.nh_list[
            direction].dist < particle.own_dist) and not particle.particle_in(direction) and \
                not particle.tile_in(direction) and particle.prev_direction != direction:
            possible_directions.append((direction, particle.nh_list[direction].dist))
    if len(possible_directions) > 0:
        nearest_free_location = min(possible_directions, key=lambda x: x[1])
        if particle.p_max.dist > particle.own_dist or nearest_free_location[1] < particle.own_dist \
                and (not(particle.keep_distance) or nearest_free_location[1] <= particle.own_dist):
            return nearest_free_location[0]
    return False
