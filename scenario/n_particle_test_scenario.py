from lib.tile import gray, blue, red, black


def scenario(sim):
    sim.add_location(0, 0)

    # This value determines the length of the hexagon's sides
    hexagon_scale_factor = 12
    outer_hexagon_radius = hexagon_scale_factor * 2

    # This sets the out-most tiles of the hexagon
    sim.add_tile(outer_hexagon_radius/2, outer_hexagon_radius, color=gray)
    sim.add_tile(outer_hexagon_radius, 0, color=blue)
    sim.add_tile(outer_hexagon_radius/2, -outer_hexagon_radius, color=gray)
    sim.add_tile(-outer_hexagon_radius/2, -outer_hexagon_radius, color=gray)
    sim.add_tile(-outer_hexagon_radius, 0, color=red)
    sim.add_tile(-outer_hexagon_radius/2, outer_hexagon_radius, color=gray)

    # This constructs all the six sides of the hexagon
    for i in range(1, outer_hexagon_radius):
        sim.add_tile(-outer_hexagon_radius/2 + i, outer_hexagon_radius, color=gray)
        sim.add_tile(outer_hexagon_radius/2 + (0.5*i), outer_hexagon_radius - i, color=blue)
        sim.add_tile(outer_hexagon_radius/2 + (0.5*i), -outer_hexagon_radius + i, color=blue)
        sim.add_tile(-outer_hexagon_radius/2 + i, -outer_hexagon_radius, color=gray)
        sim.add_tile(-outer_hexagon_radius/2 - (0.5*i), -outer_hexagon_radius + i, color=red)
        sim.add_tile(-outer_hexagon_radius/2 - (0.5*i), outer_hexagon_radius - i, color=red)

    # This adds the location for the finishing line
    sim.add_location(outer_hexagon_radius/2, 0, color=blue)
    for i in range(1, int(outer_hexagon_radius/2)):
        sim.add_location(outer_hexagon_radius / 2, i * 2, color=blue)
        sim.add_location(outer_hexagon_radius / 2, i * -2, color=blue)

    for tile in sim.tiles:
        if tile.color == [0.8, 0.0, 0.0]:
            tile.write_memory_with("light_emission", 1)

    radius = 1  # This value determines the radius of the particle hexagon that is to be created
    sim.add_particle(0, 0, color=red)
    displacement = - radius + 0.5
    iteration = 0
    for i in range(1, radius+1):
        sim.add_particle( i, 0)
        sim.add_particle(-i, 0)
    for i in range(1, radius+1):
        for j in range(0, (2*radius) - iteration):
            sim.add_particle(displacement + j, i)
            sim.add_particle(displacement + j, -i)
        iteration = iteration + 1
        displacement = displacement + 0.5


