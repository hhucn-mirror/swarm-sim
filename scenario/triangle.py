def scenario(sim):
    sim.add_tile(0, 0)
    sim.add_tile(-1.0, 0.0)
    sim.add_tile(-0.5, 1.0)
    for tile in sim.tiles:
        sim.add_location(tile.coords[0] + 0.5, tile.coords[1] + 1)
        sim.add_location(tile.coords[0] + 0.5, tile.coords[1] - 1)
        sim.add_location(tile.coords[0] - 0.5, tile.coords[1] + 1)
        sim.add_location(tile.coords[0] - 0.5, tile.coords[1] - 1)
        sim.add_location(tile.coords[0]+ 1, tile.coords[1] )
        sim.add_location(tile.coords[0]- 1, tile.coords[1] )

    for tile in sim.tiles:
        for location in sim.locations:
            if tile.coords == location.coords:
                sim.remove_location_on(location.coords)

    for i in range (1, len(sim.locations)+1):
        sim.add_particle(i, 0)

    # sim.add_particle(1.5, 1.0)
    # sim.add_particle(0.5, 1.0)
    # sim.add_particle(1.0, -0.0)
    # sim.add_particle(0.5, -1.0)
    # sim.add_particle(1.5, -1.0)
    # sim.add_particle(2.0, 0.0)
    # sim.add_particle(2.5, 1.0)
    # sim.add_particle(2.5, -1.0)
    # sim.add_particle(2.0, 2.0)
    # sim.add_particle(3.0, 2.0)
    # sim.add_particle(3.5, 1.0)
    # sim.add_particle(4.0, -0.0)
    # sim.add_particle(4.5, -1.0)
    # sim.add_particle(3.5, -1.0)
    # sim.add_particle(3.0, -2.0)
    # sim.add_particle(2.0, -2.0)
    # sim.add_particle(1.0, -2.0)
    # sim.add_particle(1.0, 2.0)
    # sim.add_particle(3.0, -0.0)
