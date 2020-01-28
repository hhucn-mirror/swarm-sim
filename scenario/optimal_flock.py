from lib.swarm_sim_header import black, get_hexagon_coordinates
from lib.world import World


def scenario(world: World):
    radius = world.config_data.flock_radius
    centre = (-10, -10)

    hexagon = get_hexagon_coordinates(centre, radius)
    for l in hexagon:
        world.add_particle(coordinates=l, color=black)
