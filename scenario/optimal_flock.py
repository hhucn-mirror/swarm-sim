def scenario(sim):
    radius = 1
    centre = (0, 0)

    hexagon = get_hexagon_coordinates(centre, radius)
    for l in hexagon:
        sim.add_particle(l[0], l[1])


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
