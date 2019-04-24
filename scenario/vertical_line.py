import copy

E = 0
SE = 1
SW = 2
W = 3
NW = 4
NE = 5
S = 6  # S for stop and not south

direction = [E, SE, SW, W, NW, NE]

def scenario(sim):
    sim.add_tile(0, 0)
    sim.add_tile(0.5, 1.0)
    sim.add_tile(1.0, 2.0)
    sim.add_tile(1.5, 3.0)
    sim.add_tile(2.0, 4.0)
    sim.add_tile(2.5, 5.0)
    sim.add_tile(3.0, 6.0)
    sim.add_tile(3.5, 7.0)
    sim.add_tile(4.0, 8.0)

    for tile in sim.tiles:
        sim.add_location(tile.coords[0] + 0.5, tile.coords[1] + 1)
        sim.add_location(tile.coords[0] + 0.5, tile.coords[1] - 1)
        sim.add_location(tile.coords[0] - 0.5, tile.coords[1] + 1)
        sim.add_location(tile.coords[0] - 0.5, tile.coords[1] - 1)
        sim.add_location(tile.coords[0]+ 1, tile.coords[1] )
        sim.add_location(tile.coords[0]- 1, tile.coords[1] )
    # actual_locations = copy.copy(sim.locations)
    # for location in actual_locations:
    #     sim.add_location(location.coords[0] + 0.5, location.coords[1] + 1)
    #     sim.add_location(location.coords[0] + 0.5, location.coords[1] - 1)
    #     sim.add_location(location.coords[0] - 0.5, location.coords[1] + 1)
    #     sim.add_location(location.coords[0] - 0.5, location.coords[1] - 1)
    #     sim.add_location(location.coords[0]+ 1, location.coords[1] )
    #     sim.add_location(location.coords[0]- 1, location.coords[1] )


    for tile in sim.tiles:
        for location in sim.locations:
            location.alpha = 0.1
            if tile.coords == location.coords:
                sim.remove_location_on(location.coords)

    for i in range (1, len(sim.locations) + 1 ):
        sim.add_particle(i, 0)
