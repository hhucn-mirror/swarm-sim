from lib.tile import gray, blue, red, black


def scenario(sim):
    sim.add_location(0, 0)
    value = 24  # This value determines the length of the hexagon's sides
    sim.add_tile(value/2, value, color=gray)
    sim.add_tile(value, 0, color=blue)
    sim.add_tile(value/2, -value, color=gray)
    sim.add_tile(-value/2, -value, color=gray)
    sim.add_tile(-value, 0, color=red)
    sim.add_tile(-value/2, value, color=gray)

    for i in range(1, value):
        sim.add_tile(-value/2 + i, value, color=gray)
        sim.add_tile(value/2 + (0.5*i), value - i, color=blue)
        sim.add_tile(value/2 + (0.5*i), -value + i, color=blue)
        sim.add_tile(-value/2 + i, -value, color=gray)
        sim.add_tile(-value/2 - (0.5*i), -value + i, color=red)
        sim.add_tile(-value/2 - (0.5*i), value - i, color=red)

    sim.add_location(value/2, 0, color=blue)
    for i in range(1, int(value/2)):
        sim.add_location(value / 2, i * 2, color=blue)
        sim.add_location(value / 2, i * -2, color=blue)

    for tile in sim.tiles:
        if tile.color == [0.8, 0.0, 0.0]:
            tile.write_memory_with("light_emission", 2)

    radius = 3  # This value determines the radius of the particle hexagon that is to be created
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


