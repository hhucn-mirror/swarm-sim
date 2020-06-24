import sys
from math import copysign

import numpy as np

# colors
black = (0, 0, 0, 1)
gray = (128, 128, 128, 1)
red = (255, 0, 0, 1)
green = (0, 128, 0, 1)
blue = (0, 0, 255, 1)
yellow = (255, 255, 0, 1)
orange = (255, 165, 0, 1)
cyan = (0, 255, 255, 1)
purple = (128, 0, 128, 1)


def eeprint(*args, sep=' ', end='\n'):
    """
    prints error message to stderr, stops the program with error code -1
    :param args: like in print()
    :param sep: like in print()
    :param end: like in print()
    :return:
    """
    print(*args, sep, end, file=sys.stderr)
    exit(-1)


def eprint(*args, sep=' ', end='\n'):
    """
    prints error message to stderr
    :param args: like in print()
    :param sep: like in print()
    :param end: like in print()
    :return:
    """
    print(*args, sep, end, file=sys.stderr)


def get_coordinates_in_direction(coordinates, direction):
    """
    Returns the coordinates data of the pointed directions

    :param coordinates: particles actual staying coordination
    :param direction: The direction. Options:  E, SE, SW, W, NW, or NE
    :return: The coordinates of the pointed directions
    """
    return coordinates[0] + direction[0], coordinates[1] + direction[1], coordinates[2] + direction[2]


def get_surrounding_coordinates(coordinates):
    surroundings = []
    for direction in [(1, 0, 0), (-1, 0, 0), (0.5, 1, 0), (-0.5, 1, 0), (0.5, -1, 0), (-0.5, -1, 0)]:
        surroundings.append(get_coordinates_in_direction(coordinates, direction))
    return surroundings


def get_multiple_steps_in_direction(start, direction, steps):
    """
    returns coordinates of the point from the start variable in x steps in the given direction
    :param start: the starting point
    :param direction: the direction
    :param steps: the amount of steps
    :return: coordinates (float, float, float)
    """
    return start[0] + (direction[0] * steps), start[1] + (direction[1] * steps), start[2] + (direction[2] * steps)


def scan_in(matter_map: dict, center, hop, grid):
    result = []
    n_sphere_border = grid.get_n_sphere_border(center, hop)
    for l in n_sphere_border:
        if l in matter_map and l != center:
            result.append(matter_map[l])
    return result


def free_locations(matter_map: dict, center, hop, grid):
    result = []
    n_sphere_border = grid.get_n_sphere_border(center, hop)
    for l in n_sphere_border:
        if l not in matter_map:
            result.append(l)
    return result


def free_locations_within_hops(matter_map: dict, center, hop, grid):
    result = []
    n_sphere_border = grid.get_n_sphere(center, hop)
    for l in n_sphere_border:
        if l not in matter_map:
            result.append(l)
    return result


def scan_within(matter_map, center, hop, grid):
    result = []
    n_sphere_border = grid.get_n_sphere(center, hop)
    for l in n_sphere_border:
        if l in matter_map and l != center:
            result.append(matter_map[l])
    return result


def taken_locations(matter_map, center, hop, grid):
    result = []
    n_sphere_border = grid.get_n_sphere(center, hop)
    for l in n_sphere_border:
        if l in matter_map and l != center:
            result.append(l)
    return result


def scan_within_per_hop(matter_map, center, max_hop, grid):
    result = []
    for hop in range(0, max_hop + 1):
        within_hop = scan_in(matter_map, center, hop, grid)
        if within_hop:
            result.append(within_hop)
    return result


def create_matter_in_line(world, start, direction, amount, matter_type='particle'):
    current_position = start
    for _ in range(amount):
        if matter_type == 'particle':
            world.add_particle(current_position)
        elif matter_type == 'tile':
            world.add_tile(current_position)
        elif matter_type == 'location':
            world.add_location(current_position)
        else:
            print("create_matter_in_line: unknown type (allowed: particle, tile or location")
            return
        current_position = get_coordinates_in_direction(current_position, direction)


def get_hexagon_coordinates(centre, r_max, exclude_centre=False):
    """
    Returns all locations of a 2d-hexagon with centre :param centre: and radius :param r_max:.
    :param exclude_centre: should the centre coordinate be included
    :type exclude_centre: boolean
    :param centre: the centre location of the hexagon
    :type centre: tuple
    :param r_max: radius of the hexagon
    :type r_max: int
    :return: list of locations
    :rtype: list
    """
    locations = []
    if not exclude_centre:
        locations.append(centre)
    displacement = - r_max + 0.5
    iteration = 0
    for y in range(1, r_max + 1):
        locations.append((centre[0] + y, centre[1], 0))
        locations.append(((centre[0] - y), centre[1], 0))
        for x in range(0, (2 * r_max) - iteration):
            locations.append((centre[0] + displacement + x, centre[1] + y, 0))
            locations.append((centre[0] + displacement + x, centre[1] - y, 0))
        iteration = iteration + 1
        displacement = displacement + 0.5
    return locations


def get_hexagon_ring(centre, r_max):
    """
    Returns all locations of a 2d-hexagon ring with centre :param centre: and radius :param r_max:.
    :param centre: the centre location of the hexagon
    :type centre: tuple
    :param r_max: radius of the hexagon
    :type r_max: int
    :return: list of locations
    :rtype: list
    """
    locations = []
    for x, y in zip(np.arange(r_max * 0.5, r_max + 0.5, 0.5),
                    np.arange(r_max, -1, -1)):
        locations.append((x + centre[0], y + centre[1], centre[2]))
        locations.append((x + centre[0], -y + centre[1], centre[2]))
        locations.append((-x + centre[0], y + centre[1], centre[2]))
        locations.append((-x + centre[0], -y + centre[1], centre[2]))
    for x in np.arange(-(r_max * 0.5), r_max * 0.5, 0.5):
        locations.append((x + centre[0], r_max + centre[1], centre[2]))
        locations.append((x + centre[0], -r_max + centre[1], centre[2]))
    return locations


def vector_angle(u: np.ndarray, v: np.ndarray, beta=False, degrees=False):
    denominator = np.linalg.norm(u) * np.linalg.norm(v)
    if denominator == 0:
        phi = 1 / 2 * np.pi
    else:
        phi = np.arccos(u.dot(v) / denominator)
    if beta:
        phi = 2 * np.pi - phi
    if degrees:
        return np.rad2deg(phi)
    return phi


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
