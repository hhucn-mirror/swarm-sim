import copy

def scenario(sim):
    sim.add_tile(0.0, 2.0)
    sim.add_tile(3.0, 2.0)
    sim.add_tile(0.5, 3.0)
    sim.add_tile(1.5, 3.0)
    sim.add_tile(2.5, 3.0)
    sim.add_tile(3.5, 1.0)
    sim.add_tile(3.0, 0.0)
    sim.add_tile(0.0, 0.0)
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
    print("Number of locations", len(sim.locations))
    for i in range (3, len(sim.locations)+3):
        sim.add_particle (i+1, 0)
    print("Number of Particles", len(sim.particles))