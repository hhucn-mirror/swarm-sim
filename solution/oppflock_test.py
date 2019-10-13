import collections
import operator
import random

from lib.oppnet.mobility_model import MobilityModel, Mode
from lib.std_lib import NE, SE, E, NW, SW, W


def solution(sim):
    particles = sim.get_particle_list()

    if sim.get_actual_round() == 1:
        # mobility model for the moving particle
        # make it move back and forth between the two borders
        # head east first
        m_model = MobilityModel(particles[0].coords[0], particles[0].coords[1], mode=Mode.Random,
                                length=(10, 10), starting_dir=E)
        m_model.set(particles[0])

    elif sim.get_actual_round() % 2:

        # move the first particle
        m_model = MobilityModel.get(particles[0])
        next_direction = m_model.next_direction(current_x_y=particles[0].coords)
        if next_direction is not False:
            while next_direction_taken(particles[0], next_direction):
                create_alleyway(particles[0], next_direction)
            particles[0].move_to_in_bounds(next_direction)

    else:
        next_directions = calculate_next_directions(particles[1:], particles[0].coords)
        for particle, next_direction in next_directions.items():
            if next_direction is not False:
                particle.move_to_in_bounds(next_direction)


def create_alleyway(centroid, next_centroid_direction):
    next_coords = centroid.sim.get_coords_in_dir(centroid.coords, next_centroid_direction)
    prev_coords = next_coords
    particle_map_coords = centroid.sim.get_particle_map_coords()

    while next_coords in particle_map_coords:
        prev_coords = next_coords
        next_coords = centroid.sim.get_coords_in_dir(next_coords, next_centroid_direction)

    particle = particle_map_coords[prev_coords]
    not_taken = not_taken_locations(particle)
    if not_taken:
        random_coords = random.choice(list(not_taken))
        particle.move_to(direction_from_coordinates(particle.coords, random_coords))


def not_taken_locations(particle):
    nearby_particles = particle.scan_for_particle_within()
    one_hops = calculate_surrounding_one_hop_coordinates(particle.coords)
    if nearby_particles:
        for nearby in nearby_particles:
            one_hops.difference(nearby.coords)
    return one_hops


def next_direction_taken(centroid, next_centroid_direction):
    next_coords = centroid.sim.get_coords_in_dir(centroid.coords, next_centroid_direction)
    return next_coords in centroid.sim.get_particle_map_coords()


def all_surroundings_taken(particle):
    return len(particle.scan_for_particle_within()) == 6


def calculate_next_directions(particles, centroid_coordinates):
    next_directions = {}
    next_coordinates = calculate_next_coordinates(particles, centroid_coordinates)
    for coordinates, [particle, _] in next_coordinates.items():
        next_directions[particle] = direction_from_coordinates(particle.coords, coordinates)
    return next_directions


def direction_from_coordinates(start, destination):
    # east
    if start[0] < destination[0]:
        # north
        if start[1] < destination[1]:
            return NE
        elif start[1] > destination[1]:
            return SE
        else:
            return E
    # west
    elif start[0] > destination[0]:
        # north
        if start[1] < destination[1]:
            return NW
        elif start[1] > destination[1]:
            return SW
        else:
            return W
    else:
        return False


def calculate_next_coordinates(particles, centroid_coordinates):
    distance_dicts = calculate_all_coordinates_and_distances(particles, centroid_coordinates)

    next_coordinates = {}
    remaining_particles = set(particles)
    dict_index = 0

    while remaining_particles and dict_index < 6:
        for particle in list(remaining_particles):
            distance_dict = distance_dicts[particle]
            coordinates, distance = list(distance_dict.items())[dict_index]
            remaining_particles = update_next_coordinates(coordinates, dict_index, distance, distance_dict,
                                                          distance_dicts, next_coordinates, particle,
                                                          remaining_particles)
        dict_index += 1
    return next_coordinates


def update_next_coordinates(coordinates, dict_index, distance, distance_dict, distance_dicts, next_coordinates,
                            particle, remaining_particles):
    if coordinates not in next_coordinates:
        next_coordinates[coordinates] = [particle, distance]
        remaining_particles -= {particle}
    else:
        remaining_particles = coordinates_exist(coordinates, dict_index, distance, distance_dict, distance_dicts,
                                                next_coordinates, particle, remaining_particles)
    return remaining_particles


def coordinates_exist(coordinates, dict_index, distance, distance_dict, distance_dicts, next_coordinates, particle,
                      remaining_particles):
    [current_particle, current_distance] = next_coordinates.get(coordinates)
    if current_distance > distance:
        next_coordinates.update({coordinates: [particle, distance]})
        remaining_particles -= {particle}
    elif current_distance == distance:
        current_distance_dict = distance_dicts[current_particle]
        if next_current_is_smaller(current_distance_dict, distance_dict, dict_index + 1):
            next_coordinates.update({coordinates: [particle, distance]})
            remaining_particles -= {particle}
            remaining_particles |= {current_particle}
    return remaining_particles


def next_current_is_smaller(current_distance_dict, new_distance_dict, index):
    if index > len(current_distance_dict.values()) or len(new_distance_dict.values()):
        return False
    next_distance_current = list(current_distance_dict.values())[index]
    next_distance_new = list(new_distance_dict.values())[index]
    return next_distance_current < next_distance_new


def calculate_all_coordinates_and_distances(particles, centroid_coordinates):
    distance_dicts = {}
    for particle in particles:
        distances = calculate_zero_and_one_hop_distances(particle, centroid_coordinates)
        distance_dicts[particle] = distances
    return distance_dicts


def calculate_one_hop_overlap(particle, neighbour):
    particle_surroundings = calculate_surrounding_one_hop_coordinates(particle.coords)
    neighbour_surroundings = calculate_surrounding_one_hop_coordinates(neighbour.coords)
    return particle_surroundings.intersection(neighbour_surroundings)


def calculate_zero_and_one_hop_distances(particle, centroid_coordinates):
    one_hop_coordinates = calculate_surrounding_one_hop_coordinates(particle.coords)
    one_hop_coordinates -= {centroid_coordinates}
    one_hop_distances = {}
    for coordinates in one_hop_coordinates:
        one_hop_distances[coordinates] = calculate_distance(coordinates, centroid_coordinates)
    # add own zero hop distance
    one_hop_distances[particle.coords] = calculate_distance(particle.coords, centroid_coordinates)

    sorted_tuples = sorted(one_hop_distances.items(), key=operator.itemgetter(1))

    return collections.OrderedDict(sorted_tuples)


def calculate_surrounding_one_hop_coordinates(coordinates):
    x, y = coordinates
    return {(x - 1, y), (x + 1, y), (x - 0.5, y - 1), (x + 0.5, y - 1), (x - 0.5, y + 1), (x + 0.5, y + 1)}


def calculate_distance(coordinates_1, coordinates_2):
    x1, y1 = coordinates_1[0], coordinates_1[1]
    x2, y2 = coordinates_2[0], coordinates_2[1]
    x_diff = abs(x2 - x1)
    y_diff = abs(y2 - y1)

    if y1 == y2 and x1 != x2:
        return x_diff
    elif (x_diff - y_diff * 0.5) > 0:
        return y_diff + (x_diff - y_diff * 0.5)
    else:
        return y_diff
