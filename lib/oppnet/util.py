from math import copysign

from lib.oppnet.leader_flocking.opp_particle import Particle
from lib.oppnet.point import Point


def all_pairs_flock_distance(flock: [Particle]):
    """
    Calculates the all pairs distance sum in a flock :param flock.
    :param flock: list of particles
    :return: all pairs distances sum for a flock
    """
    all_pairs_distance = 0
    for particle1, particle2 in zip(flock, flock):
        all_pairs_distance += get_distance_from_points(particle1.get_coordinates_as_point(),
                                                       particle2.get_coordinates_as_point())
    return all_pairs_distance


def optimal_flock_distance(flock_radius):
    """
    Calculates the all pairs distance sum for every particle in a flock with radius :param flock_radius.
    :param flock_radius: the radius of the flock
    :return: all pair distances sum for all particles in a flock
    """
    optimal_distance = 0
    for flock_radius_in in range(0, flock_radius + 1):
        optimal_distance += optimal_flock_in_in_distance(flock_radius_in)
        for flock_radius_out in [radius for radius in range(0, flock_radius) if radius != flock_radius_in]:
            optimal_distance += optimal_flock_in_out_distance(flock_radius_in, flock_radius_out)
    return optimal_distance


def optimal_flock_in_in_distance(flock_radius):
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


def get_direction_between_coordinates(coordinates1, coordinates2):
    x_diff, y_diff = coordinates1[0] - coordinates2[0], coordinates1[1] - coordinates2[1]
    # north
    if y_diff != 0:
        y_diff = copysign(1, y_diff)
    else:
        y_diff = 0
    if x_diff != 0:
        x_diff = copysign(1 - (abs(y_diff) * 0.5), x_diff)
    else:
        x_diff = 0
    return x_diff, y_diff, 0

