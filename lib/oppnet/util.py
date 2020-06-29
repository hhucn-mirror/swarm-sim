import math

import numpy as np

from lib.oppnet.point import Point


def all_pairs_flock_distance(flock_coordinates):
    """
    Calculates the all pairs distance sum of a iterable of coordinates :param flock_coordinates.
    :param flock_coordinates: iterable of particle coordinates
    :return: all pairs distances sum for a flock
    """
    all_pairs_distance = 0
    for coordinates1, coordinates2 in zip(flock_coordinates, flock_coordinates):
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
    for flock_radius_in in range(0, flock_radius + 1):
        optimal_distance += optimal_flock_in_distance(flock_radius_in)
        for flock_radius_out in [radius for radius in range(0, flock_radius) if radius != flock_radius_in]:
            optimal_distance += optimal_flock_in_out_distance(flock_radius_in, flock_radius_out)
    return optimal_distance


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
    if flock_radius_in != 0:
        return 2 * (5 * flock_radius_in ** 3 + (18 * flock_radius_out ** 2 + 1) * flock_radius_in)
    else:
        return 6 * flock_radius_out ** 2


def flock_uniformity(flock_directions):
    """
    Calculates the uniformity of particles in terms of current velocity vectors.
    :param flock_directions: iterable of directions
    :return: the flock's uniformity
    """
    x_sum = y_sum = 0
    for particle_direction in flock_directions:
        x, y, _ = particle_direction
        x_sum += x
        y_sum += y
    if len(flock_directions) > 0:
        return abs(x_sum) / len(flock_directions), abs(y_sum) / len(flock_directions)
    else:
        return 0, 0


def flock_spread(flock_coordinates, norm, grid):
    """
    Calculates the spread of particles in terms of distance to the center and uses :param norm as norm.
    :param flock_coordinates: iterable of particle coordinates
    :param norm: the norm to calculate a pairwise distance
    :param grid: a grid object
    :return: the flock's spread
    """
    spread = 0
    center_coordinates = get_coordinates_center(flock_coordinates, grid)
    for particle_coordinates in flock_coordinates:
        spread += norm(particle_coordinates, center_coordinates)
    if len(flock_coordinates) > 0:
        return spread / len(flock_coordinates)
    else:
        return 0


def eucledian_norm(coordinates1, coordinates2):
    """
    Returns the eucledian norm of :param coordinates1 and :param coordinates2.
    :param coordinates1: first coordinates
    :param coordinates2: second coordinates
    :return: eucledian norm
    """
    x_1, y_1 = coordinates1
    x_2, y_2 = coordinates2
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
    x = (max_values[0] - min_values[0]) / 2
    y = (max_values[1] - min_values[0]) / 2
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
