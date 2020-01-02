import sys
import random
import math
debug = 0
debug_write = 0
debug_read = 0
debug_p_max_calculation = 0
debug_distance_calculation = 0
debug_movement = 0
direction_list = [0, 1, 2, 3, 4, 5]
direction_to_coords = [(0.5, 1, 0),
                       (1, 0, 0),
                       (0.5, -1, 0),
                       (-0.5, -1, 0),
                       (-1, 0, 0),
                       (-0.5, 1, 0)]


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
    if hasattr(direction, "__getitem__"):
        return coordinates[0] + direction[0], coordinates[1] + direction[1], coordinates[2] + direction[2]
    else:
        return coordinates[0] + direction_to_coords[direction][0], coordinates[1] + direction_to_coords[direction][1],\
               coordinates[2] + direction_to_coords[direction][2]


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


def generating_random_spraded_particles(world, max_size_particle):
    for _ in range(0, max_size_particle):
        x = random.randrange(-world.get_world_x_size(), world.get_world_x_size())
        y = random.randrange(-world.get_world_y_size(), world.get_world_y_size())
        if y % 2 == 1:
            x = x + 0.5
        if (x, y) not in world.tile_map_coordinates:
            world.add_particle((x, y))


def move_to_dest_step_by_step(particle, destiny, directions, prev_dir=None):
    """

    :param particle:
    :param destiny:
    :param directions
    :param prev_dir
    :return: True if movement occured, False if not movment and a Matter if the next direction point has a matter on it
    """
    next_dir = get_next_direction_to(particle.coordinates[0], particle.coordinates[1],
                                     destiny.coordinates[0], destiny.coordinates[1], directions)
    if next_dir in prev_dir:
        return None
    if particle.tile_in(next_dir) or particle.particle_in(next_dir):
        particle.get_matter_in(next_dir)
        return particle.get_matter_in(next_dir)
    particle.move_to(next_dir)
    if debug and debug_movement:
        print("\n P", particle.number, " moves to", direction_number_to_string(next_dir))
    return False


def get_next_direction_to(src_x, src_y, dest_x, dest_y, directions):
    """
    :param src_x: x coordinate of the source
    :param src_y: y coordinate of the source
    :param dest_x: x coordinate of the destiny
    :param dest_y: y coordinate of the destiny
    :return: the next direction that brings the matter closer to the destiny
    """
    next_dir = -1
    if (src_x < dest_x or src_x == dest_x) and src_y < dest_y:
        next_dir = directions["NE"]
    elif src_y < dest_y and src_x > dest_x:
        next_dir = directions["NW"]
    elif src_y > dest_y and src_x < dest_x:
        next_dir = directions["SE"]
    elif (src_x > dest_x or src_x == dest_x) and src_y > dest_y:
        next_dir = directions["SW"]
    elif src_y == dest_y and src_x > dest_x:
        next_dir = directions["W"]
    elif src_y == dest_y and src_x < dest_x:
        next_dir = directions["E"]
    return next_dir


def get_the_invert(direction):
    return (direction + 3) % 6


def direction_in_range(direction):
    return direction % 6
