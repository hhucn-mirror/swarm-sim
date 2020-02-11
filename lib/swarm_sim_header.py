import sys

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
        if l in matter_map:
            result.append(matter_map[l])
    return result


def free_locations(matter_map: dict, center, hop, grid):
    result = []
    n_sphere_border = grid.get_n_sphere_border(center, hop)
    for l in n_sphere_border:
        if l not in matter_map:
            result.append(l)
    return result


def scan_within(matter_map, center, hop, grid):
    result = []
    n_sphere_border = grid.get_n_sphere(center, hop)
    for l in n_sphere_border:
        if l in matter_map:
            result.append(matter_map[l])
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
