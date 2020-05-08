from lib.swarm_sim_header import get_hexagon_coordinates, black
from lib.world import World


def scenario(world: World):
    radius = world.config_data.flock_radius
    centre = (0, 0)
    hexagon = get_hexagon_coordinates(centre, radius)

    if world.config_data.particle_color is None:
        particle_color = black
    else:
        particle_color = world.config_data.particle_color

    for location in hexagon:
        world.add_particle(coordinates=location, color=particle_color)
