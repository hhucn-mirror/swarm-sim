import math
from itertools import product

import numpy as np

from lib.oppnet.point import Point
from lib.swarm_sim_header import get_hexagon_ring


def all_pairs_flock_distance(flock_coordinates):
    """
    Calculates the all pairs distance sum of a iterable of coordinates :param flock_coordinates.
    :param flock_coordinates: iterable of particle coordinates
    :return: all pairs distances sum for a flock
    """
    all_pairs_distance = 0
    for coordinates1, coordinates2 in product(flock_coordinates, repeat=2):
        all_pairs_distance += get_distance_from_coordinates(coordinates1, coordinates2)
    return all_pairs_distance


def get_max_flock_radius(particles_count):
    """
    Calculates the maximum flock radius of an optimally shaped flock with :param particles_count many particles.
    :param particles_count: the number of particles
    :return: maximum radius of an optimally shaped flock
    """
    return math.sqrt(particles_count / 3 - 1 / 12) - 1 / 2


def optimal_flock_distance(flock_radius):
    """
    Calculates the all pairs distance sum for every particle in a flock with radius :param flock_radius.
    :param flock_radius: the radius of the flock
    :return: all pair distances sum for all particles in a flock
    """
    optimal_distance = 0
    flock_radius = int(flock_radius)
    hexagon_rings = get_all_hexagon_rings_as_list(range(0, flock_radius + 1))
    for flock_radius_in in range(0, flock_radius + 1):
        optimal_distance += optimal_flock_in_distance(flock_radius_in)
        for flock_radius_out in [radius for radius in range(0, flock_radius + 1) if radius != flock_radius_in]:
            optimal_distance += optimal_in_out_distance_locations(hexagon_rings[flock_radius_in],
                                                                  hexagon_rings[flock_radius_out])
    return optimal_distance


def get_all_hexagon_rings_as_list(radius_range):
    """
    Returns a list of hexagon rings with radii defined by range :param radius_range.
    :param radius_range: range object of radii
    :return: a list of hexagon rings as location sets
    """
    rings = []
    for radius in radius_range:
        rings.append(get_hexagon_ring((0, 0, 0), radius))
    return rings


def optimal_in_out_distance_locations(hexagon_1, hexagon_2):
    """
    Calculates the optimal distance sum between all pairs of particles between two hexagon rings
    (grids/TriangularGrid.py) :param hexagon_1 and radius :param hexagon_2.
    :param hexagon_1: the first hexagon as set of locations
    :param hexagon_2: the second hexagon as set of locations
    :return: all pairs distance sum
    """
    all_pairs_distance = 0
    for l1 in hexagon_1:
        for l2 in hexagon_2:
            all_pairs_distance += get_distance_from_coordinates(l1, l2)
    return all_pairs_distance


def optimal_flock_in_distance(flock_radius):
    """
    Calculates the all pairs distance sum between particles in a hexagon ring with radius :param flock_radius.
    :param flock_radius: the radius of the hexagon ring
    :return: the sum of all pair distances in the hexagon ring
    """
    return 46 * flock_radius ** 3 + 2 * flock_radius


def optimal_flock_in_out_distance(flock_radius_in, flock_radius_out):
    """
    Calculates the optimal distance sum between all pairs of particles in a hexagon ring (grids/TriangularGrid.py) of
    radius of radius :param flock_radius_out and radius :param flock_radius_in,
    where :param flock_radius_in < :param flock_radius_out. Pairs contain a particle in the inner and outer ring each.
    :param flock_radius_in: radius of the smaller, inner ring in a hexagon
    :param flock_radius_out: radius of the larger, outer ring in a hexagon
    :return: the sum of all pair distances between outer and inner hexagon ring
    """
    ring_in = get_hexagon_ring((0, 0, 0), flock_radius_in)
    ring_out = get_hexagon_ring((0, 0, 0), flock_radius_out)
    all_pairs_distance = 0
    for l1 in ring_in:
        for l2 in ring_out:
            all_pairs_distance += get_distance_from_coordinates(l1, l2)
    return all_pairs_distance


def flock_uniformity(flock_directions):
    """
    Calculates the uniformity of particles in terms of current velocity vectors.
    :param flock_directions: iterable of directions
    :return: the flock's uniformity
    """
    x_sum = y_sum = 0
    for particle_direction in flock_directions:
        if particle_direction is None:
            x = y = 0
        else:
            x, y, _ = particle_direction
        x_sum += x
        y_sum += y
    if len(flock_directions) > 0:
        return abs(x_sum) / len(flock_directions), abs(y_sum) / len(flock_directions)
    else:
        return 0, 0


def flock_spread(flock_coordinates, grid):
    """
    Calculates the spread of particles in terms of distance to the center and uses both euclidean and hops distance
    as norm.
    :param flock_coordinates: iterable of particle coordinates
    :param grid: a grid object
    :return: the flock's spread with euclidean norm and hop distance norm
    """
    spread_euclidean = spread_hops = 0
    center_coordinates = get_coordinates_center(flock_coordinates, grid)
    for particle_coordinates in flock_coordinates:
        spread_euclidean += euclidean_norm(particle_coordinates, center_coordinates)
        spread_hops += get_distance_from_coordinates(particle_coordinates, center_coordinates)
    if len(flock_coordinates) > 0:
        return spread_euclidean / len(flock_coordinates), spread_hops / len(flock_coordinates), center_coordinates
    else:
        return 0


def euclidean_norm(coordinates1, coordinates2):
    """
    Returns the euclidean norm of :param coordinates1 and :param coordinates2.
    :param coordinates1: first coordinates
    :param coordinates2: second coordinates
    :return: euclidean norm
    """
    x_1, y_1, _ = coordinates1
    x_2, y_2, _ = coordinates2
    return math.sqrt((x_1 - x_2) ** 2 + (y_1 - y_2) ** 2)


def get_coordinates_center(particle_coordinates, grid):
    """
    Returns the nearest valid coordinates of an estimated center of all coordinate properties in :param particles.
    :param particle_coordinates: iterable of particle coordinates
    :param grid: a grid object
    :return: nearest valid coordinates of the particles coordinate center
    """
    max_values = np.max(particle_coordinates, axis=0)
    min_values = np.min(particle_coordinates, axis=0)
    x = (max_values[0] + min_values[0]) / 2
    y = (max_values[1] + min_values[1]) / 2
    return grid.get_nearest_valid_coordinates((x, y, 0))


def get_distance_from_points(position1: Point, position2: Point):
    """
    Calculates the hop distance between two coordinate tuples.
    :param position1: first coordinates as Point
    :param position2: second coordinates as Point
    :return: hop distance between two coordinates
    """
    x1, y1 = position1.getx(), position1.gety()
    x2, y2 = position2.getx(), position2.gety()
    x_diff = abs(x2 - x1)
    y_diff = abs(y2 - y1)

    if y1 == y2 and x1 != x2:
        return x_diff
    elif (x_diff - y_diff * 0.5) > 0:
        return y_diff + (x_diff - y_diff * 0.5)
    else:
        return y_diff


def get_distance_from_coordinates(coordinates1: tuple, coordinates2: tuple):
    """
    Calculates the hop distance between two coordinate tuples.
    :param coordinates1: first coordinates
    :param coordinates2: second coordinates
    :return: hop distance between two coordinates
    """
    x_diff = abs(coordinates2[0] - coordinates1[0])
    y_diff = abs(coordinates2[1] - coordinates1[1])

    if coordinates1[1] == coordinates2[1] and coordinates1[0] != coordinates2[0]:
        return x_diff
    elif (x_diff - y_diff * 0.5) > 0:
        return y_diff + (x_diff - y_diff * 0.5)
    else:
        return y_diff
