import math
import numpy as np
from lib.swarm_sim_header import *


def end_sim(sim):
    if goal_reached(sim):
        if complete_check(sim):
            sim.set_successful_end()
            # own_dists = np.array([p.own_dist for p in sim.particles])
            # unique, counts = np.unique(own_dists, return_counts=True)
            # print(dict(zip(unique, counts)))
            if sim.config_data.visualization:
                print("successful end reached after round:", sim.get_actual_round())


def goal_reached(sim):
    min_fl_distance = min(list(map(get_smallest_fl, sim.particles)), default=0)
    # print("asd", max((particle.own_dist for particle in sim.particles), default=math.inf))
    # print("qwe", (particle.own_dist for particle in sim.particles))
    max_particle_distance = max((particle.own_dist for particle in sim.particles), default=math.inf)
    if min_fl_distance is math.inf or min_fl_distance < max_particle_distance:
        return False
    else:
        return True


def get_smallest_fl(particle):
    return min((neighbor.dist for neighbor in particle.nh_list if neighbor.type == "fl"), default=math.inf)


def complete_check(world):
    particle_distance_list = []
    locations_distance_list = []
    for particle in world.particles:
        for direction in world.grid.get_directions_list():
            if not particle.matter_in(direction):
                locations_distance_list.append(get_closest_tile_distance(
                    get_coordinates_in_direction(particle.coordinates, direction), world))
        particle_distance_list.append(get_closest_tile_distance(particle.coordinates, world))
    if particle_distance_list and locations_distance_list:
        if max(particle_distance_list) <= min(locations_distance_list):
            return True
    return False


def get_closest_tile_distance(source, world):
    return min((world.grid.get_distance(source, tile.coordinates) for tile in world.get_tiles_list()))


