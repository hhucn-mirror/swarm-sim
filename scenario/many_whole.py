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
    sim.add_tile(2.0, 10.0)
    sim.add_tile(1.5, 9.0)
    sim.add_tile(1.0, 8.0)
    sim.add_tile(0.5, 7.0)
    sim.add_tile(-0.0, 6.0)
    sim.add_tile(-0.5, 5.0)
    sim.add_tile(-1.5, 5.0)
    sim.add_tile(-2.5, 5.0)
    sim.add_tile(-3.5, 5.0)
    sim.add_tile(-4.0, 6.0)
    sim.add_tile(-3.5, 7.0)
    sim.add_tile(-2.5, 7.0)
    sim.add_tile(-1.5, 7.0)
    sim.add_tile(-1.0, 8.0)
    sim.add_tile(-0.5, 9.0)
    sim.add_tile(-1.5, 9.0)
    sim.add_tile(-2.0, 10.0)
    sim.add_tile(-1.5, 11.0)
    sim.add_tile(-0.5, 11.0)
    sim.add_tile(0.5, 11.0)

    for tile in sim.tiles:
        sim.add_marker(tile.coords[0] + 0.5, tile.coords[1] + 1)
        sim.add_marker(tile.coords[0] + 0.5, tile.coords[1] - 1)
        sim.add_marker(tile.coords[0] - 0.5, tile.coords[1] + 1)
        sim.add_marker(tile.coords[0] - 0.5, tile.coords[1] - 1)
        sim.add_marker(tile.coords[0]+ 1, tile.coords[1] )
        sim.add_marker(tile.coords[0]- 1, tile.coords[1] )
    # actual_markers = copy.copy(sim.markers)
    # for marker in actual_markers:
    #     sim.add_marker(marker.coords[0] + 0.5, marker.coords[1] + 1)
    #     sim.add_marker(marker.coords[0] + 0.5, marker.coords[1] - 1)
    #     sim.add_marker(marker.coords[0] - 0.5, marker.coords[1] + 1)
    #     sim.add_marker(marker.coords[0] - 0.5, marker.coords[1] - 1)
    #     sim.add_marker(marker.coords[0]+ 1, marker.coords[1] )
    #     sim.add_marker(marker.coords[0]- 1, marker.coords[1] )


    for tile in sim.tiles:
        for marker in sim.markers:
            marker.alpha = 0.1
            if tile.coords == marker.coords:
                sim.remove_marker_on(marker.coords)

    for i in range (1, len(sim.markers)+1):
        if i == 2:
            sim.add_particle(i, 6, color=3)
        else:
            sim.add_particle(i, 6)
    # sim.add_particle (1.0, 0.0)
    # sim.add_particle  (1.5, 1.0)
    # sim.add_particle  (2.0, 0.0)
    # sim.add_particle  (2.5, 1.0)
    # sim.add_particle  (3.0, -0.0)
    # sim.add_particle  (3.5, 1.0)
    # sim.add_particle  (4.0, -0.0)

    # sim.add_particle(1.5, 1.0)
    # sim.add_particle(0.5, 1.0)
    # sim.add_particle(1.0, -0.0)
    # sim.add_particle(0.5, -1.0)
    # sim.add_particle(1.5, -1.0)
    # sim.add_particle(2.0, 0.0)
    # sim.add_particle(2.5, 1.0)
    # sim.add_particle(2.5, -1.0)
