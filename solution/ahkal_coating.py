import logging
import math
import random
import sys
import copy
from copy import deepcopy
import collections

black = 1
gray = 2
red = 3
green = 4
blue = 5
yellow = 6
orange = 7
cyan = 8
violett = 9

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5

direction = [NE, E, SE, SW, W, NW]


def invert_dir(dir):
    if dir >= 3:
        return dir - 3
    else:
        return dir + 3


def dir_in_range(dir):
    if dir > 5:
        return dir - 6
    elif dir < 0:
        return dir + 6
    return dir


def check_for_particle(particle):
    particle_dir_list = []
    for dir in direction:
        if particle.particle_in(dir):
            particle_dir_list.append(dir)
            # print("Found tile in dir ", dir)

    return particle_dir_list


def check_for_free_locations(particle):
    location_dir_list = []
    for dir in direction:
        if not particle.tile_in(dir) and not particle.particle_in(dir):
            location_dir_list.append(dir)
    if len(location_dir_list) != 0:
        return location_dir_list
    else:
        return location_dir_list


def check_only_for_tile(particle):
    tile_dir_list = []
    for dir in direction:
        if particle.tile_in(dir):
            tile_dir_list.append(dir)
            # print("Found tile in dir ", dir)
    if len(tile_dir_list) != 0:
        return tile_dir_list
    else:
        return tile_dir_list


def dir_str(dir):
    if dir == 0:
        return "NO"
    elif dir == 1:
        return "O"
    elif dir == 2:
        return "SO"
    elif dir == 3:
        return "SW"
    elif dir == 4:
        return "W"
    elif dir == 5:
        return "NW"
    elif dir == -1:
        return "Error"


debug = True
debug2 = True


class neighbors:
    def __init__(self, type, dist):
        self.type = type
        self.dist = dist


class info_package:
    def __init__(self, own_dist, ml_min_dist, ml_dir, ml_hop, p_max_dist, p_dir, p_hop):
        self.own_dist = own_dist
        self.ml_min_dist = ml_min_dist
        self.ml_dir = ml_dir
        self.ml_hop = ml_hop
        self.p_max_dist = p_max_dist
        self.p_dir = p_dir
        self.p_hop = p_hop


def reset_attributes(particle):
    particle.ml_min_dist = 10000
    particle.ml_hop = 0
    particle.p_max_dist = -1
    particle.p_hop = 0
    particle.NH_dict.clear()
    particle.ml_cnt = 0
    particle.t_cnt = 0


cycle_no = 4


def getCoordsOfNearestTile(partilceCoords, sim):
    tileCoords = sim.get_tile_map_coords()

    # max float
    min = 1.7976931348623157e+308
    x = sim.get_sim_x_size()
    y = sim.get_sim_y_size()
    for tCoords in tileCoords:
        xdiff = partilceCoords[0] - tCoords[0]
        ydiff = partilceCoords[1] - tCoords[1]
        value = math.sqrt((xdiff * xdiff) + (ydiff * ydiff))
        if (value < min):
            min = value
            x = tCoords[0]
            y = tCoords[1]
    return (x, y)


def countToTile(particle, tile_coords, sim):
    counter = 0
    prev_n_dir = NW
    prev_s_dir = SW
    phantom_coords = (particle.coords[0], particle.coords[1])
    while phantom_coords != tile_coords:
        if phantom_coords[1] < tile_coords[1] and phantom_coords[0] < \
                tile_coords[0]:
            phantom_coords = sim.get_coords_in_dir(phantom_coords, NE)
            counter += 1
        elif phantom_coords[1] < tile_coords[1] and phantom_coords[0] > \
                tile_coords[0]:
            phantom_coords = sim.get_coords_in_dir(phantom_coords, NW)
            counter += 1
        elif phantom_coords[1] > tile_coords[1] and phantom_coords[0] < \
                tile_coords[0]:
            phantom_coords = sim.get_coords_in_dir(phantom_coords, SE)
            counter += 1
        elif phantom_coords[1] > tile_coords[1] and phantom_coords[0] > \
                tile_coords[0]:
            phantom_coords = sim.get_coords_in_dir(phantom_coords, SW)
            counter += 1
        else:
            if phantom_coords[1] == tile_coords[1]:
                if phantom_coords[0] > tile_coords[0]:
                    phantom_coords = sim.get_coords_in_dir(phantom_coords, W)
                    counter += 1
                elif phantom_coords[0] < tile_coords[0]:
                    phantom_coords = sim.get_coords_in_dir(phantom_coords, E)
                    counter += 1
            elif phantom_coords[1] < tile_coords[1]:
                if prev_n_dir == NW:
                    phantom_coords = sim.get_coords_in_dir(phantom_coords, NE)
                    prev_n_dir = NE
                    counter += 1
                else:
                    phantom_coords = sim.get_coords_in_dir(phantom_coords, NW)
                    prev_n_dir = NW
                    counter += 1
            elif phantom_coords[1] > tile_coords[1]:
                if prev_s_dir == SW:
                    phantom_coords = sim.get_coords_in_dir(phantom_coords, SE)
                    prev_s_dir = SE
                    counter += 1
                else:
                    phantom_coords = sim.get_coords_in_dir(phantom_coords, SW)
                    prev_s_dir = SW
                    counter += 1
    return counter


def check_layer_coated(sim):
    free_locations = len(sim.locations)
    occ_locations_cnt = 0
    for location in sim.locations:
        for particle in sim.particles:
            if particle.coords == location.coords:
                occ_locations_cnt += 1
    if free_locations == occ_locations_cnt:
        print("Success")
        return True
    else:
        return False


def create_new_particles(sim):
    particles_list = []
    max_x = -10000
    coords = ()
    for location in sim.locations:
        if location.coords[0] > max_x:
            max_x = location.coords[0]
            coords = location.coords
    if coords in sim.location_map_coords:
        sim.location_map_coords[coords].set_color(blue)
    if coords[0] % 1 != 0:
        print(coords[0])
        start_i = int(coords[0] - 0.5)
        for i in range(start_i, len(sim.locations) + start_i):
            new_particle = sim.add_particle(i + 0.5, coords[1])
            if new_particle:
                initialize_particle(new_particle)
                particles_list.append(new_particle)
    else:
        for i in range(int(coords[0]), len(sim.locations) + int(coords[0])):
            new_particle = sim.add_particle(i, coords[1])
            if new_particle:
                initialize_particle(new_particle)
                particles_list.append(new_particle)
    return particles_list


layer = 0


def new_marked_locations(sim):
    global layer
    if layer == 0:
        for tile in sim.tiles:
            sim.add_location(tile.coords[0] + 0.5, tile.coords[1] + 1)
            sim.add_location(tile.coords[0] + 0.5, tile.coords[1] - 1)
            sim.add_location(tile.coords[0] - 0.5, tile.coords[1] + 1)
            sim.add_location(tile.coords[0] - 0.5, tile.coords[1] - 1)
            sim.add_location(tile.coords[0] + 1, tile.coords[1])
            sim.add_location(tile.coords[0] - 1, tile.coords[1])

        for tile in sim.tiles:
            for location in sim.locations:
                if tile.coords == location.coords:
                    sim.remove_location_on(location.coords)
        layer = 1
    else:
        actual_locations = sim.locations.copy()
        location_cnt = 0
        for location in actual_locations:
            if sim.add_location(location.coords[0] + 0.5, location.coords[1] + 1):
                location_cnt += 1
            if sim.add_location(location.coords[0] + 0.5, location.coords[1] - 1):
                location_cnt += 1
            if sim.add_location(location.coords[0] - 0.5, location.coords[1] + 1):
                location_cnt += 1
            if sim.add_location(location.coords[0] - 0.5, location.coords[1] - 1):
                location_cnt += 1
            if sim.add_location(location.coords[0] + 1, location.coords[1]):
                location_cnt += 1
            if sim.add_location(location.coords[0] - 1, location.coords[1]):
                location_cnt += 1
            # if first_round:
            #     coords = location.coords
            #     first_round = False
            #     continue
            # elif coords[0] < location.coords[0]:
            #     coords = location.coords
            sim.remove_location_on(location.coords)
        for tile in sim.tiles:
            for location in sim.locations:
                if tile.coords == location.coords:
                    sim.remove_location_on(location.coords)
        for particle in sim.particles:
            particle.set_color(red)
            sim.red_particles.append(particle)
            for location in sim.locations:
                if particle.coords == location.coords:
                    sim.remove_location_on(location.coords)
        layer = layer + 1


def coating_complete(sim, particles_list):
    global layer
    max_hop = -1
    for particle in particles_list:
        hop = countToTile(particle, getCoordsOfNearestTile(particle.coords, sim), sim)
        if hop > max_hop:
            max_hop = hop
    print("At round ", sim.get_actual_round(), " the max particle hop is ", max_hop)
    if max_hop <= layer:
        print("Success ", max_hop, layer)
        return True
    return False


termination = True
new_layer = True
particles_list = []


def solution(sim):
    """
    A coating cycle consist of five rounds.

    """
    global new_layer, particles_list
    # if exit_start:
    #     if exit_cnt==0:
    #         sim.success_termination()
    #     exit_cnt -= 1
    #     return

    if new_layer:
        new_marked_locations(sim)
        particles_list = create_new_particles(sim)
        new_layer = False
    else:
        # new_layer = check_layer_coated(sim)
        new_layer = coating_complete(sim, particles_list)

    """
        new_phase
        check if layer_coated or sim.get_actual_round() == 1:
            yes: new_phase=True
        else:
            new_phase=False
        check if new_phase
        if yes 
            create new_locations
            create new_particles

    """
    for particle in particles_list:
        if sim.get_actual_round() == 1:
            setattr(sim, "red_particles", [])
            setattr(sim, "green_particles", [])
            initialize_particle(particle)

        if sim.get_actual_round() % cycle_no == 1:
            """ 
            First round of the coating cylce

            In this round each particle checks its neighborhood and stores in its NH_dict 
            the type of the neighbor. If the particle is beside a tile then it gives itself the distance of one
            """
            scanning_neighborhood(particle, sim, particles_list)

            if debug:
                print("\n", sim.get_actual_round())
                print("P", particle.number, "after scanning neighborhood")
                print("distance", particle.own_dist, "postition", particle.coords)
                if debug2:
                    print("Dir|Type|Distance|Hop")
                    for dir in particle.NH_dict:
                        print(dir_str(dir), "|", particle.NH_dict[dir].type,
                              "|", particle.NH_dict[dir].dist)
                print("ml_min_dist", particle.ml_min_dist, "ml_dir", dir_str(particle.ml_dir),
                      "ml_hop", particle.ml_hop)
                print("p_max_dist", particle.p_max_dist, "p_dir", dir_str(particle.p_dir), "p_hop", particle.p_hop)

                # if you got your own distance
        elif sim.get_actual_round() % cycle_no == 2:
            """
            3rd round of the coating cycle:
            In this round each particle gives all the free locations that are beside a tile a distance
            and initialized based on that information the free location that has a minumum distance
            After that it reads its rcv_buffer. If the sender particle has a distance
            the distances of the free locations of the receiver particle will be defined. 
            At the end it compares its local information with the received informations.
            """

            """
            Because of debugging reason the data_settings is happing in this round
            """
            if debug:
                print("P", particle.number, "Before checked received Information")
            data_setting(particle)
            if debug:
                print("distance", particle.own_dist)
                if debug2:
                    print("Dir|Type|Distance|Hop")
                    for dir in particle.NH_dict:
                        print(dir_str(dir), "|", particle.NH_dict[dir].type,
                              "|", particle.NH_dict[dir].dist)
                print("ml_min_dist =", particle.ml_min_dist, "ml_dir =", dir_str(particle.ml_dir), "ml_hop =",
                      particle.ml_hop)
                print("p_max_dist = ", particle.p_max_dist, "p_dir = ", dir_str(particle.p_dir), "p_hop =  ",
                      particle.p_hop, "waiting state", particle.wait)

            if not particle.wait and check_data_received(particle):
                update_local_data(particle)

                if debug:
                    print("\n after defined the distances of your neighborhood ml ")
                    print("ml_min_dist =", particle.ml_min_dist, "ml_dir =", dir_str(particle.ml_dir), "ml_hop =",
                          particle.ml_hop)
                    print("p_max_dist =", particle.p_max_dist, "p_dir =", dir_str(particle.p_dir), "p_hop =",
                          particle.p_hop)
            else:
                particle.wait = False
            particle.delete_whole_memeory()
            particle.rcv_buf.clear()
            if debug:
                print("P", particle.number, "After checked received Information")
                print("distance", particle.own_dist)
                if debug2:
                    print("Dir|Type|Distance|Hop")
                    for dir in particle.NH_dict:
                        print(dir_str(dir), "|", particle.NH_dict[dir].type,
                              "|", particle.NH_dict[dir].dist)
                print("ml_min_dist =", particle.ml_min_dist, "ml_dir =", dir_str(particle.ml_dir),
                      "ml_hop =", particle.ml_hop)
                print("p_max_dist = ", particle.p_max_dist, "p_dir = ", dir_str(particle.p_dir), "p_hop =  ",
                      particle.p_hop, "waiting state", particle.wait)
        elif sim.get_actual_round() % cycle_no == 3:
            data_sending(particle)
        elif sim.get_actual_round() % cycle_no == 0:
            moving_decision(particle, sim)


def initialize_particle(particle):
    """
            At the first starting round of the simulator:
            Initialize each particles with new attributes and values.
            """
    # dist: distance
    setattr(particle, "own_dist", 10000)
    # ml: free location; min: minimum
    setattr(particle, "ml_min_dist", 10000)
    # dir: direction
    setattr(particle, "ml_dir", None)
    setattr(particle, "ml_hop", 0)
    # p: particle
    setattr(particle, "p_max_dist", -1)
    setattr(particle, "p_dir", None)
    setattr(particle, "p_hop", 0)
    # NH: neighborhood
    # In the the NH_dict the key is the direction of the neighbor and the data is an object of the class
    # neighbor in the the type, distance, and hop of the neighborhood matter is stored
    setattr(particle, "NH_dict", {})
    # rcv: receiver, buf: buffer
    setattr(particle, "rcv_buf", {})
    # free location counter
    setattr(particle, "ml_cnt", 0)
    # tile counter
    setattr(particle, "t_cnt", 0)
    # stores the previous (prev) direction
    setattr(particle, "prev_dir", -1)
    setattr(particle, "wait", False)


def scanning_neighborhood(particle, sim, particles_list):
    reset_attributes(particle)
    scan_nh(particle, sim, particles_list)


def scan_nh(particle, sim, particles_list):
    circle = False
    for dir in direction:
        if particle.particle_in(dir):
            if particle.get_matter_in_dir(matter="particle", dir=dir).get_color() == red:
                particle.NH_dict[dir] = neighbors("t", 0)
                particle.t_cnt += 1
            else:
                particle.NH_dict[dir] = neighbors("p", -1)
            circle = circle_check(circle, dir, particle, particles_list, sim)
        elif particle.tile_in(dir):
            particle.NH_dict[dir] = neighbors("t", 0)
            # particle.own_dist = 1  #You are beside a tile so you become a distance
            # particle.p_max_dist = 1 #And at the beginning the p_max is always your own distance
            # if you are beside a tile you clear your ml list because it is not needed to store them
            particle.t_cnt += 1
        elif particle.location_in(dir):
            particle.NH_dict[dir] = neighbors("ml", 10000)
            particle.ml_cnt += 1
        else:
            particle.NH_dict[dir] = neighbors("fl", 10000)

    if circle == True:
        for dir in direction:
            if particle.particle_in(dir):
                if particle.get_matter_in_dir(matter="particle", dir=dir).get_color() == black:
                    particle.get_matter_in_dir(matter="particle", dir=dir).set_color(orange)


def circle_check(circle, dir, particle, particles_list, sim):
    if (particle.get_color() == orange or particle.get_color() == yellow) and \
            particle.get_matter_in_dir(matter="particle", dir=dir).get_color() == black \
            and particle.get_matter_in_dir(matter="particle", dir=dir).check_on_location():
        particle.get_matter_in_dir(matter="particle", dir=dir).set_color(orange)
    if particle.get_color() == orange and \
            particle.get_matter_in_dir(matter="particle", dir=dir).get_color() == green \
            and particle.get_matter_in_dir(matter="particle", dir=dir).check_on_location():
        print("Circles is closed")
        # for location in sim.locations:
        #     if location.get_color() == blue:
        #         sim.remove_location_on(location.coords)
        for par in particles_list:
            if par.get_color() == green or par.get_color() == orange \
                    or par.get_color() == yellow:
                par.set_color(blue)
        for loc in sim.locations.copy():
            if loc.get_color() == blue:
                if sim.remove_location_on(loc.coords) == False:
                    pass
    if particle.get_color() == violett \
            and particle.get_matter_in_dir(matter="particle", dir=dir).get_color() == violett:
        print("Circle")
        circle = True
        particle.set_color(yellow)
        particle.get_matter_in_dir(matter="particle", dir=dir).set_color(green)
    return circle


def data_setting(particle):
    if get_own_dist(particle):
        if particle.t_cnt != 0:
            set_nh_dist(particle)
            set_min_max_data(particle)
            return True
    return False


def get_own_dist(particle):
    if particle.t_cnt > 0:
        print("P ", particle.number, "got the distance 1")
        particle.own_dist = 1
        return True
    elif particle.own_dist != 10000:
        return True
    return False


def set_nh_dist(particle):
    for dir in particle.NH_dict:
        if particle.NH_dict[dir_in_range(dir)].type == "t":
            if particle.t_cnt == 1:
                for i in range(1, 3):
                    particle.NH_dict[dir_in_range(dir + i)].dist = i
                    particle.NH_dict[dir_in_range(dir - i)].dist = i
                particle.NH_dict[dir_in_range(dir + 3)].dist = 2
            elif particle.t_cnt == 2:
                if particle.NH_dict[dir_in_range(dir + 1)].type == "t":
                    particle.NH_dict[dir_in_range(dir + 1)].dist = 0
                    particle.NH_dict[dir_in_range(dir - 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir + 2)].dist = 1
                    particle.NH_dict[dir_in_range(dir - 2)].dist = 2
                    particle.NH_dict[dir_in_range(dir + 3)].dist = 2
                elif particle.NH_dict[dir_in_range(dir - 1)].type == "t":
                    particle.NH_dict[dir_in_range(dir - 1)].dist = 0
                    particle.NH_dict[dir_in_range(dir + 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir - 2)].dist = 1
                    particle.NH_dict[dir_in_range(dir + 2)].dist = 2
                    particle.NH_dict[dir_in_range(dir + 3)].dist = 2
                elif particle.NH_dict[dir_in_range(dir + 2)].type == "t":
                    particle.NH_dict[dir_in_range(dir + 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir - 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir + 2)].dist = 0
                    particle.NH_dict[dir_in_range(dir - 2)].dist = 2
                    particle.NH_dict[dir_in_range(dir + 3)].dist = 1
                elif particle.NH_dict[dir_in_range(dir - 2)].type == "t":
                    particle.NH_dict[dir_in_range(dir - 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir + 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir - 2)].dist = 0
                    particle.NH_dict[dir_in_range(dir + 2)].dist = 2
                    particle.NH_dict[dir_in_range(dir + 3)].dist = 1
                elif particle.NH_dict[dir_in_range(dir + 3)].type == "t":
                    particle.NH_dict[dir_in_range(dir + 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir - 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir + 2)].dist = 1
                    particle.NH_dict[dir_in_range(dir - 2)].dist = 1
                    particle.NH_dict[dir_in_range(dir + 3)].dist = 0
            elif particle.t_cnt == 3:
                if particle.NH_dict[dir_in_range(dir + 1)].type == "t":
                    if particle.NH_dict[dir_in_range(dir + 2)].type == "t":
                        particle.NH_dict[dir_in_range(dir + 1)].dist = 0
                        particle.NH_dict[dir_in_range(dir - 1)].dist = 1
                        particle.NH_dict[dir_in_range(dir + 2)].dist = 0
                        particle.NH_dict[dir_in_range(dir + 3)].dist = 1
                        particle.NH_dict[dir_in_range(dir - 2)].dist = 2
                    elif particle.NH_dict[dir_in_range(dir - 1)].type == "t":
                        particle.NH_dict[dir_in_range(dir + 1)].dist = 0
                        particle.NH_dict[dir_in_range(dir - 1)].dist = 0
                        particle.NH_dict[dir_in_range(dir + 2)].dist = 1
                        particle.NH_dict[dir_in_range(dir + 3)].dist = 2
                        particle.NH_dict[dir_in_range(dir - 2)].dist = 1
                    elif particle.NH_dict[dir_in_range(dir + 3)].type == "t":
                        particle.NH_dict[dir_in_range(dir + 1)].dist = 0
                        particle.NH_dict[dir_in_range(dir - 1)].dist = 1
                        particle.NH_dict[dir_in_range(dir + 2)].dist = 1
                        particle.NH_dict[dir_in_range(dir + 3)].dist = 0
                        particle.NH_dict[dir_in_range(dir - 2)].dist = 1
                    elif particle.NH_dict[dir_in_range(dir - 2)].type == "t":
                        particle.NH_dict[dir_in_range(dir + 1)].dist = 0
                        particle.NH_dict[dir_in_range(dir - 1)].dist = 1
                        particle.NH_dict[dir_in_range(dir + 2)].dist = 1
                        particle.NH_dict[dir_in_range(dir + 3)].dist = 1
                        particle.NH_dict[dir_in_range(dir - 2)].dist = 0
                elif particle.NH_dict[dir_in_range(dir - 1)].type == "t":
                    if particle.NH_dict[dir_in_range(dir - 2)].type == "t":
                        particle.NH_dict[dir_in_range(dir - 1)].dist = 0
                        particle.NH_dict[dir_in_range(dir + 1)].dist = 1
                        particle.NH_dict[dir_in_range(dir - 2)].dist = 0
                        particle.NH_dict[dir_in_range(dir + 3)].dist = 1
                        particle.NH_dict[dir_in_range(dir + 2)].dist = 2
                    elif particle.NH_dict[dir_in_range(dir + 1)].type == "t":
                        particle.NH_dict[dir_in_range(dir + 1)].dist = 0
                        particle.NH_dict[dir_in_range(dir - 1)].dist = 0
                        particle.NH_dict[dir_in_range(dir + 2)].dist = 1
                        particle.NH_dict[dir_in_range(dir + 3)].dist = 2
                        particle.NH_dict[dir_in_range(dir - 2)].dist = 1
                    elif particle.NH_dict[dir_in_range(dir + 3)].type == "t":
                        particle.NH_dict[dir_in_range(dir + 1)].dist = 1
                        particle.NH_dict[dir_in_range(dir - 1)].dist = 0
                        particle.NH_dict[dir_in_range(dir + 2)].dist = 1
                        particle.NH_dict[dir_in_range(dir + 3)].dist = 0
                        particle.NH_dict[dir_in_range(dir - 2)].dist = 1
                    elif particle.NH_dict[dir_in_range(dir + 2)].type == "t":
                        particle.NH_dict[dir_in_range(dir + 1)].dist = 1
                        particle.NH_dict[dir_in_range(dir - 1)].dist = 0
                        particle.NH_dict[dir_in_range(dir + 2)].dist = 0
                        particle.NH_dict[dir_in_range(dir + 3)].dist = 1
                        particle.NH_dict[dir_in_range(dir - 2)].dist = 1
                elif particle.NH_dict[dir_in_range(dir + 3)].type == "t":
                    if particle.NH_dict[dir_in_range(dir - 2)].type == "t":
                        particle.NH_dict[dir_in_range(dir - 1)].dist = 1
                        particle.NH_dict[dir_in_range(dir + 1)].dist = 1
                        particle.NH_dict[dir_in_range(dir - 2)].dist = 0
                        particle.NH_dict[dir_in_range(dir + 3)].dist = 0
                        particle.NH_dict[dir_in_range(dir + 2)].dist = 1
                    if particle.NH_dict[dir_in_range(dir - 2)].type == "t":
                        particle.NH_dict[dir_in_range(dir - 1)].dist = 1
                        particle.NH_dict[dir_in_range(dir + 1)].dist = 1
                        particle.NH_dict[dir_in_range(dir - 2)].dist = 1
                        particle.NH_dict[dir_in_range(dir + 3)].dist = 0
                        particle.NH_dict[dir_in_range(dir + 2)].dist = 0
                else:
                    particle.NH_dict[dir_in_range(dir - 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir + 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir - 2)].dist = 0
                    particle.NH_dict[dir_in_range(dir + 3)].dist = 1
                    particle.NH_dict[dir_in_range(dir + 2)].dist = 0
            elif particle.t_cnt >= 4:
                for i in range(1, 6):
                    if particle.NH_dict[dir_in_range(dir + i)].type == "t":
                        particle.NH_dict[dir_in_range(dir + i)].dist = 0
                    else:
                        particle.NH_dict[dir_in_range(dir + i)].dist = 1
            return


def get_nh_dist(particle, dir):
    nh_dist_dict = {}
    nh_dist_frw = particle.NH_dict[dir_in_range(dir + 1)].dist
    nh_type_frw = particle.NH_dict[dir_in_range(dir + 1)].type
    nh_dist_bkw = particle.NH_dict[dir_in_range(dir - 1)].dist
    nh_type_bkw = particle.NH_dict[dir_in_range(dir - 1)].type

    if nh_type_frw == "p":
        if nh_dist_frw != -1:
            nh_dist_dict[dir_in_range(dir + 1)] = nh_dist_frw
    if nh_type_bkw == "p":
        if nh_dist_bkw != -1:
            nh_dist_dict[dir_in_range(dir - 1)] = nh_dist_bkw

    if nh_type_frw == "t":
        nh_dist_dict[dir_in_range(dir + 1)] = 0
    if nh_type_bkw == "t":
        nh_dist_dict[dir_in_range(dir - 1)] = 0

    if nh_type_frw == "ml":
        if nh_dist_frw != 10000:
            nh_dist_dict[dir_in_range(dir + 1)] = nh_dist_frw
    if nh_type_bkw == "ml":
        if nh_dist_bkw != 10000:
            nh_dist_dict[dir_in_range(dir - 1)] = nh_dist_bkw

    return nh_dist_dict


def set_min_max_data(particle):
    for dir in particle.NH_dict:
        if particle.NH_dict[dir].type == "p":
            if particle.p_max_dist < particle.NH_dict[dir].dist:
                particle.p_max_dist = particle.NH_dict[dir].dist
                particle.p_dir = dir
                particle.p_hop = 1
        if particle.NH_dict[dir].type == "ml":
            if particle.NH_dict[dir].dist < particle.ml_min_dist:
                if particle.prev_dir != dir or particle.ml_cnt == 1:
                    particle.ml_min_dist = particle.NH_dict[dir].dist
                    particle.ml_dir = dir
                    particle.ml_hop = 1


def check_data_received(particle):
    if particle.read_whole_memory():
        particle.rcv_buf = particle.read_whole_memory()
        return True
    return False


def update_local_data(particle):
    # if particle.own_dist == 10000:
    if get_own_dist_from_nh(particle):
        update_nh_dict(particle)
    comparing_ml_p_dist(particle)


def get_own_dist_from_nh(particle):
    p_dist_dict = {}
    for dir in particle.rcv_buf:
        if particle.rcv_buf[dir].own_dist != 10000:
            """
                  Take the distances of the neighborhood particles and store them in a list
            """
            p_dist_dict[dir] = particle.rcv_buf[dir].own_dist

    if p_dist_dict:
        # Give yourself a distance if you are not beside a tile
        # particle.own_dist = min(p_dist_list, key=p_dist_list.get)+1
        if min(p_dist_dict.values()) + 1 < particle.own_dist:
            print(" P", particle.number, "changed its distance from", particle.own_dist, " to ",
                  min(p_dist_dict.values()) + 1)
            particle.own_dist = min(p_dist_dict.values()) + 1
        return True
        # print("min is Equal ", p_ml_min_dist_dict.values())
    return False


def update_nh_dict(particle):
    for dir in particle.rcv_buf:
        if debug:
            print("\n the sender from direction", dir_str(invert_dir(dir)), "sent following data:")
            print("Own distance ", particle.rcv_buf[dir].own_dist, "ml_min_dist =",
                  particle.rcv_buf[dir].ml_min_dist, "ml_dir =", dir_str(particle.rcv_buf[dir].ml_dir),
                  "ml_hop =", particle.rcv_buf[dir].ml_hop,
                  "p_max_dist = ", particle.rcv_buf[dir].p_max_dist,
                  "p_dir = ", dir_str(particle.rcv_buf[dir].p_dir),
                  "p_hop =  ", particle.rcv_buf[dir].p_hop)
        if particle.rcv_buf[dir].own_dist != 10000 and particle.t_cnt == 0:
            if particle.NH_dict[dir_in_range(invert_dir(dir) + 1)].type == "p":
                particle.NH_dict[invert_dir(dir)].dist = particle.rcv_buf[dir].own_dist
            if particle.NH_dict[dir_in_range(invert_dir(dir) + 1)].type == "ml":
                particle.NH_dict[dir_in_range(invert_dir(dir) + 1)].dist = particle.rcv_buf[dir].own_dist + 1
            if particle.NH_dict[dir_in_range(invert_dir(dir) - 1)].type == "ml":
                particle.NH_dict[dir_in_range(invert_dir(dir) - 1)].dist = particle.rcv_buf[dir].own_dist + 1

            # update = True
            # # if update == True:
            # #     #set_nh_dist(particle)
            # #     set_min_max_data(particle)


def comparing_ml_p_dist(particle):
    for dir in particle.rcv_buf:
        # only accept data for ml from particles that have a lower distance than you.
        find_min_ml(dir, particle)
        # Check for the for the particle that has the highest distance
        find_max_p(dir, particle)
    # if particle.p_max_dist == -1:
    #     particle.ml_dir = None


def find_min_ml(dir, particle):
    if particle.rcv_buf[dir].ml_min_dist < particle.ml_min_dist:  # got the sender a smaller ml?
        new_ml(dir, particle)
    # if the distances are the same
    elif particle.rcv_buf[dir].ml_min_dist == particle.ml_min_dist:
        # comparing hop_counts
        hop_compare(dir, particle)


def find_max_p(dir, particle):
    if particle.p_max_dist == -1 and particle.rcv_buf[dir].own_dist < particle.own_dist:
        particle.p_max_dist = particle.own_dist
        particle.p_dir = None
        particle.p_hop = 0
    if particle.rcv_buf[dir].own_dist != 10000 and particle.rcv_buf[dir].own_dist > particle.p_max_dist:
        particle.p_max_dist = particle.rcv_buf[dir].own_dist
        particle.p_dir = invert_dir(dir)
        particle.p_hop = particle.rcv_buf[dir].p_hop + 1
    elif particle.rcv_buf[dir].p_max_dist > particle.p_max_dist:
        particle.p_max_dist = particle.rcv_buf[dir].p_max_dist
        particle.p_dir = invert_dir(dir)
        particle.p_hop = particle.rcv_buf[dir].p_hop + 1
    elif particle.rcv_buf[dir].p_max_dist == particle.p_max_dist:
        if (particle.rcv_buf[dir].p_hop + 1) < particle.p_hop:
            particle.p_dir = invert_dir(dir)
            particle.p_hop = particle.rcv_buf[dir].p_hop + 1


def new_ml(dir, particle):
    if particle.prev_dir != invert_dir(dir):
        particle.ml_min_dist = particle.rcv_buf[dir].ml_min_dist
        particle.ml_dir = invert_dir(dir)
        particle.ml_hop = particle.rcv_buf[dir].ml_hop + 1


def hop_compare(dir, particle):
    if (particle.rcv_buf[dir].ml_hop + 1) < particle.ml_hop:
        new_ml(dir, particle)


def data_sending(particle):
    """
            4th round of the coating cylce:
            Each particle will share its information with its neighbors
            """
    package = info_package(particle.own_dist, particle.ml_min_dist, particle.ml_dir,
                           particle.ml_hop, particle.p_max_dist, particle.p_dir, particle.p_hop)
    for dir in direction:
        if particle.particle_in(dir):
            neighbor_p = particle.get_particle_in(dir)
            particle.write_to_with(neighbor_p, key=dir, data=deepcopy(package))
            if debug:
                print("P", particle.number, "wrote to P", neighbor_p.number, "dir", dir_str(dir))
                print("Own distance ", particle.own_dist, "ml_min_dist =",
                      particle.ml_min_dist, "ml_dir =", dir_str(particle.ml_dir),
                      "ml_hop =", particle.ml_hop, "p_max_dist = ",
                      particle.p_max_dist,
                      "p_dir = ", dir_str(particle.p_dir), "p_hop =  ", particle.p_hop)


def moving_decision(particle, sim):
    """
            5th round of the coating cylce:
            Each particle will share its information with its neighbors
            I just move if there is a free location thats distance is lower
            than a particles distance in the network.
            If I am beside a tile and get the information to move in a direction where
            there is no tile beside me I am not going to move.
    """
    if debug:
        print("\n", sim.get_actual_round())
    if particle.t_cnt > 0:
        if particle.t_cnt == 5:
            # data_clearing(particle)
            pass
        elif particle.t_cnt == 4:
            check_between_tiles(particle)
        else:
            need_to_move(particle)
    else:
        if particle.ml_dir is not None:
            check_ml_dir(particle)
        # elif particle.p_max_dist > particle.own_dist:
        #     run_from_max(particle)
        # else:
    #     need_to_move(particle
    # )


def run_from_max(particle):
    for dir in particle.NH_dict:
        if particle.NH_dict[dir].type == "ml":
            if particle.NH_dict[dir].dist == particle.p_max_dist - 1:
                if not particle.particle_in(dir):
                    moving(particle)
                    return


def check_between_tiles(particle):
    for dir in direction:
        if particle.NH_dict[dir].type == "p" and particle.NH_dict[invert_dir(dir)].type == "ml":
            if invert_dir(dir) != particle.prev_dir:
                moving(particle)
                return
        elif particle.NH_dict[dir].type == "ml" and particle.NH_dict[invert_dir(dir + 3)].type == "ml":
            if dir != particle.prev_dir and not particle.particle_in(dir) and not particle.tile_in(dir):
                moving(particle)
            elif not particle.particle_in(invert_dir(dir)) and not particle.tile_in(invert_dir(dir)):
                moving(particle)
            return
    if particle.ml_dir is not None:
        check_ml_dir(particle)


def need_to_move(particle):
    # Move to the next ml that is equal or lower than your distance
    # only if there is a particle that has an higher distance than yours.
    for dir in particle.NH_dict:
        if particle.NH_dict[dir].type == "ml":
            if particle.p_max_dist > particle.own_dist:
                if particle.NH_dict[dir].dist != 10000 and particle.NH_dict[dir].dist <= particle.own_dist:
                    if particle.prev_dir != dir:
                        if not particle.particle_in(dir):
                            moving(particle)
                            return


def check_ml_dir(particle):
    if not particle.particle_in(particle.ml_dir) and not particle.tile_in(particle.ml_dir):
        if particle.ml_dir != particle.prev_dir or particle.ml_cnt == 1:
            if particle.p_max_dist != -1 and particle.own_dist <= particle.p_max_dist:
                moving(particle)
                return True
            else:
                print(particle.number,
                      ": I do not have a maximal distance or my distance is the same with neighborhood ")
                return False
        else:
            print(particle.number, ":I do not go back or when I'm beside a tile")
            return False
    else:
        print(particle.number, ":Particle or tile is infront of me")
        return False
        # search for another free location


def moving(particle):
    if debug:
        print("\n P", particle.number, " coords before moving ", particle.coords)
    particle.move_to(particle.ml_dir)
    particle.prev_dir = invert_dir(particle.ml_dir)
    if debug:
        print("\n P", particle.number, "moved to ", dir_str(particle.ml_dir), particle.ml_dir)
        print("\n P", particle.number, " coords after moving ", particle.coords)
    data_clearing(particle)


def check_dir_dist(particle, dir):
    # if particle.NH_dict[dir].dist > particle.own_dist:
    #     return False
    return True


def data_clearing(particle):
    if particle.check_on_location():
        if particle.get_location().get_color() == black:
            particle.set_color(violett)
        particle.get_location().set_color(blue)
    particle.ml_dir = None
    particle.p_dir = None
    particle.wait = True