from lib.swarm_sim_header import green
from lib.world import World


def scenario(world: World):
    radius = 5
    centre = (0, 0)

    hexagon = get_hexagon_coordinates(centre, radius)
    for l in hexagon:
        world.add_particle(coordinates=l, color=green)


def get_hexagon_coordinates(centre, r_max):
    locations = [centre]
    displacement = - r_max + 0.5
    iteration = 0
    for i in range(1, r_max + 1):
        locations.append((i, centre[1]))
        locations.append((-i, centre[1]))
    for i in range(1, r_max + 1):
        for j in range(0, (2 * r_max) - iteration):
            locations.append((displacement + j + centre[0], i + centre[1]))
            locations.append((displacement + j + centre[0], -i + centre[1]))
        iteration = iteration + 1
        displacement = displacement + 0.5
    return locations
