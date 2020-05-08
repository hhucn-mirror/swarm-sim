import random

from lib.swarm_sim_header import get_hexagon_coordinates, black
from lib.world import World


def scenario(world: World):
    radius = world.config_data.flock_radius
    centre = (0, 0)
    hexagon = get_hexagon_coordinates(centre, radius)
    # remove a percentage of particles from the optimal flock
    removal_percentage = 0.2
    number_of_holes = round(len(hexagon) * removal_percentage)

    if world.config_data.particle_color is None:
        particle_color = black
    else:
        particle_color = world.config_data.particle_color

    # remove number_of_holes many locations from the optimal hexagon formation
    hexagon = remove_random_locations(hexagon, number_of_holes)
    for location in hexagon:
        world.add_particle(coordinates=location, color=particle_color)


def remove_random_locations(hexagon: list, number_of_locations_to_remove):
    """
    Removes :param number_of_locations_to_remove many particles randomly from the list :param hexagon and returns the
    result.
    :param hexagon: list of particles
    :param number_of_locations_to_remove: the number of particles to remove
    :return: the resulting list
    """
    total_locations = len(hexagon) - number_of_locations_to_remove
    return random.sample(hexagon, total_locations)
