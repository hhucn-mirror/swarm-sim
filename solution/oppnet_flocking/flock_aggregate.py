import random
from collections import Counter

from lib.particle import Particle


def aggregate(intended_directions):
    aggregate_directions = {}
    for particle, intended_direction in intended_directions.items():
        aggregate_directions[particle] = aggregate_direction(particle, intended_directions)
    return aggregate_directions


def aggregate_direction(particle, intended_directions):
    neighbours = neighbourhood(particle)
    direction_counter = Counter({"NE": 0, "E": 0, "SE": 0, "SW": 0, "W": 0, "NW": 0})
    if not neighbours:
        return intended_directions[particle]
    for neighbour in neighbours:
        neighbour_intended = intended_directions[neighbour]
        direction_counter[neighbour_intended] += 1
    particle_intended = intended_directions[particle]
    return most_common_dir(particle_intended, direction_counter)


def most_common_dir(particle_intended, direction_counter):
    most_commons = direction_counter.most_common()
    direction_str, direction_counter = most_commons[0]
    i = 1
    while i < len(most_commons):
        if most_commons[i] != (direction_str, direction_counter):
            break
        i += 1
    if i > 1:
        choices_list = most_commons[0:i + 1]
        weights = __choices__weights__(choices_list, particle_intended)
        choices_list.append(particle_intended)
        common_direction, _ = random.choices(choices_list, weights, k=1)
    else:
        common_direction, _ = most_commons[0]
    return common_direction


def __choices__weights__(choices, particle_intended):
    cnt = len(choices)
    weights = cnt * [0.5 / cnt]
    weights.append(particle_intended)
    return weights


def neighbourhood(particle: Particle):
    return particle.scan_for_particles_in(hop=1)
