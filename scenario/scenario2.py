def scenario(world):

    # Ameisen
    # Colony 1
    part_num = 0
    while part_num < 20:
        world.add_particle(0, 0, 1)
        part_num += 1
    # Colony 2
    part_num2 = 0
    while part_num2 < 20:
        world.add_particle(12, 0, 9)
        part_num2 += 1
    for particle in world.particles:
        print ("particle color", particle.color)

    # Futter
    world.add_tile(6, 8)
    world.add_tile(-6.5, 7)
    world.add_tile(6, -8)
    world.add_tile(-6.5, -7)
    world.add_tile(16.5, 7)
    world.add_tile(16.5, -7)

    # Base
    # Colony 1
    world.add_marker(0, 0, 1)
    # Colony 2
    world.add_marker(12, 0, 9)