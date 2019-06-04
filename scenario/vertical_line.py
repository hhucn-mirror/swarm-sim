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


    # actual_markers = copy.copy(sim.markers)
    # for marker in actual_markers:
    #     sim.add_marker(marker.coords[0] + 0.5, marker.coords[1] + 1)
    #     sim.add_marker(marker.coords[0] + 0.5, marker.coords[1] - 1)
    #     sim.add_marker(marker.coords[0] - 0.5, marker.coords[1] + 1)
    #     sim.add_marker(marker.coords[0] - 0.5, marker.coords[1] - 1)
    #     sim.add_marker(marker.coords[0]+ 1, marker.coords[1] )
    #     sim.add_marker(marker.coords[0]- 1, marker.coords[1] )

