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


def check_for_free_markers(particle):
    marker_dir_list = []
    for dir in direction:
        if not particle.tile_in(dir) and not particle.particle_in(dir):
            marker_dir_list.append(dir)
    if len(marker_dir_list) != 0:
        return marker_dir_list
    else:
        return marker_dir_list


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
    def __init__(self, own_dist, fl_min_dist, fl_dir, fl_hop, p_max_dist, p_dir, p_hop):
        self.own_dist = own_dist
        self.fl_min_dist = fl_min_dist
        self.fl_dir = fl_dir
        self.fl_hop = fl_hop
        self.p_max_dist = p_max_dist
        self.p_dir = p_dir
        self.p_hop = p_hop


def reset_attributes(particle):
    particle.fl_min_dist = 10000
    particle.fl_hop = 0
    particle.p_max_dist = -1
    particle.p_hop = 0
    particle.NH_dict.clear()
    particle.fl_cnt = 0
    particle.t_cnt = 0
    particle.own_dist = 10000


cycle_no = 4



def check_layer_coated(sim):
    free_markers = len(sim.markers)
    occ_markers_cnt = 0
    for marker in sim.markers:
        for particle in sim.particles:
            if particle.coords == marker.coords:
                occ_markers_cnt += 1
    if free_markers == occ_markers_cnt:
        print("Success")
        return True
    else:
        return False


def create_new_particles(sim):
    particles_list = []
    max_x = -10000
    coords = ()
    for marker in sim.markers:
        if marker.coords[0] > max_x:
            max_x = marker.coords[0]
            coords = marker.coords
    if coords in sim.marker_map_coords:
        sim.marker_map_coords[coords].set_color(blue)
    if coords[0] % 1 != 0:
        print(coords[0])
        start_i = int(coords[0] - 0.5)
        for i in range(start_i, len(sim.markers) + start_i + 10):
            new_particle = sim.add_particle(i + 0.5, coords[1])
            if new_particle:
                initialize_particle(new_particle)
                particles_list.append(new_particle)
    else:
        for i in range(int(coords[0]), len(sim.markers) + int(coords[0] + 10)):
            new_particle = sim.add_particle(i, coords[1])
            if new_particle:
                initialize_particle(new_particle)
                particles_list.append(new_particle)
    for marker in sim.markers.copy():
        if sim.remove_marker_on(marker.coords):
            print("Delete tile completed")
        else:
            print ("Delete tile not possible")

    return particles_list


layer = 0


def new_marked_markers(sim):
    global layer
    if layer == 0:
        for tile in sim.tiles:
            sim.add_marker(tile.coords[0] + 0.5, tile.coords[1] + 1)
            sim.add_marker(tile.coords[0] + 0.5, tile.coords[1] - 1)
            sim.add_marker(tile.coords[0] - 0.5, tile.coords[1] + 1)
            sim.add_marker(tile.coords[0] - 0.5, tile.coords[1] - 1)
            sim.add_marker(tile.coords[0] + 1, tile.coords[1])
            sim.add_marker(tile.coords[0] - 1, tile.coords[1])

        for tile in sim.tiles:
            for marker in sim.markers:
                if tile.coords == marker.coords:
                    sim.remove_marker_on(marker.coords)
        layer = 1
    else:
        actual_markers = sim.markers.copy()
        marker_cnt = 0
        for marker in actual_markers:
            if sim.add_marker(marker.coords[0] + 0.5, marker.coords[1] + 1):
                marker_cnt += 1
            if sim.add_marker(marker.coords[0] + 0.5, marker.coords[1] - 1):
                marker_cnt += 1
            if sim.add_marker(marker.coords[0] - 0.5, marker.coords[1] + 1):
                marker_cnt += 1
            if sim.add_marker(marker.coords[0] - 0.5, marker.coords[1] - 1):
                marker_cnt += 1
            if sim.add_marker(marker.coords[0] + 1, marker.coords[1]):
                marker_cnt += 1
            if sim.add_marker(marker.coords[0] - 1, marker.coords[1]):
                marker_cnt += 1
            # if first_round:
            #     coords = marker.coords
            #     first_round = False
            #     continue
            # elif coords[0] < marker.coords[0]:
            #     coords = marker.coords
            sim.remove_marker_on(marker.coords)
        for tile in sim.tiles:
            for marker in sim.markers:
                if tile.coords == marker.coords:
                    sim.remove_marker_on(marker.coords)
        for particle in sim.particles:
            particle.set_color(red)
            sim.red_particles.append(particle)
            for marker in sim.markers:
                if particle.coords == marker.coords:
                    sim.remove_marker_on(marker.coords)
        layer = layer + 1


# def coating_complete(sim, particles_list):
#     global layer
#     max_hop = -1
#     for particle in particles_list:
#         hop = countToTile(particle, getCoordsOfNearestTile(particle.coords, sim), sim)
#         if hop > max_hop:
#             max_hop = hop
#     print("At round ", sim.get_actual_round(), " the max particle hop is ", max_hop)
#     if max_hop <= layer:
#         print("Success ", max_hop, layer)
#         #sim.success_termination()
#         return True
#     return False


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

    # if new_layer:
    #     new_marked_markers(sim)
    #     particles_list = create_new_particles(sim)
    #     new_layer = False
    # else:
    #     # new_layer = check_layer_coated(sim)
    #     new_layer = coating_complete(sim, particles_list)
    if sim.get_actual_round() == 1:
        new_marked_markers(sim)
        particles_list = create_new_particles(sim)
        new_layer = False

    """
        new_phase
        check if layer_coated or sim.get_actual_round() == 1:
            yes: new_phase=True
        else:
            new_phase=False
        check if new_phase
        if yes 
            create new_markers
            create new_particles

    """
    for particle in particles_list:
        if sim.get_actual_round() == 1:
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
                print("fl_min_dist", particle.fl_min_dist, "fl_dir", dir_str(particle.fl_dir),
                      "fl_hop", particle.fl_hop)
                print("p_max_dist", particle.p_max_dist, "p_dir", dir_str(particle.p_dir), "p_hop", particle.p_hop)

                # if you got your own distance
        elif sim.get_actual_round() % cycle_no == 2:
            """
            3rd round of the coating cycle:
            In this round each particle gives all the free markers that are beside a tile a distance
            and initialized based on that information the free marker that has a minumum distance
            After that it reads its rcv_buffer. If the sender particle has a distance
            the distances of the free markers of the receiver particle will be defined. 
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
                print("fl_min_dist =", particle.fl_min_dist, "fl_dir =", dir_str(particle.fl_dir), "fl_hop =",
                      particle.fl_hop)
                print("p_max_dist = ", particle.p_max_dist, "p_dir = ", dir_str(particle.p_dir), "p_hop =  ",
                      particle.p_hop, "waiting state", particle.wait)

            if not particle.wait and check_data_received(particle):
                update_own_data_from_nh(particle)

                if debug:
                    print("\n after defined the distances of your neighborhood fl ")
                    print("fl_min_dist =", particle.fl_min_dist, "fl_dir =", dir_str(particle.fl_dir), "fl_hop =",
                          particle.fl_hop)
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
                print("fl_min_dist =", particle.fl_min_dist, "fl_dir =", dir_str(particle.fl_dir),
                      "fl_hop =", particle.fl_hop)
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
    # fl: free marker; min: minimum
    setattr(particle, "fl_min_dist", 10000)
    # dir: direction
    setattr(particle, "fl_dir", None)
    setattr(particle, "fl_hop", 0)
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
    # free marker counter
    setattr(particle, "fl_cnt", 0)
    # tile counter
    setattr(particle, "t_cnt", 0)
    # stores the previous (prev) direction
    setattr(particle, "prev_dir", -1)
    setattr(particle, "wait", False)


def scanning_neighborhood(particle, sim, particles_list):
    reset_attributes(particle)
    scan_nh(particle)


def scan_nh(particle):
    for dir in direction:
        if particle.particle_in(dir):
            particle.NH_dict[dir] = neighbors("p", -1)
        elif particle.tile_in(dir):
            particle.NH_dict[dir] = neighbors("t", 0)
            particle.t_cnt += 1
        else:
            particle.NH_dict[dir] = neighbors("fl", 10000)
            particle.fl_cnt += 1





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
                for i in range(1, 2):
                    particle.NH_dict[dir_in_range(dir + i)].dist = i
                    particle.NH_dict[dir_in_range(dir - i)].dist = i
                #particle.NH_dict[dir_in_range(dir + 3)].dist = 2
            elif particle.t_cnt == 2:
                if particle.NH_dict[dir_in_range(dir + 1)].type == "t":
                    particle.NH_dict[dir_in_range(dir + 1)].dist = 0
                    particle.NH_dict[dir_in_range(dir - 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir + 2)].dist = 1
                    #particle.NH_dict[dir_in_range(dir - 2)].dist = 2
                    #particle.NH_dict[dir_in_range(dir + 3)].dist = 2
                elif particle.NH_dict[dir_in_range(dir - 1)].type == "t":
                    particle.NH_dict[dir_in_range(dir - 1)].dist = 0
                    particle.NH_dict[dir_in_range(dir + 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir - 2)].dist = 1
                    #particle.NH_dict[dir_in_range(dir + 2)].dist = 2
                    #particle.NH_dict[dir_in_range(dir + 3)].dist = 2
                elif particle.NH_dict[dir_in_range(dir + 2)].type == "t":
                    particle.NH_dict[dir_in_range(dir + 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir - 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir + 2)].dist = 0
                    #particle.NH_dict[dir_in_range(dir - 2)].dist = 2
                    particle.NH_dict[dir_in_range(dir + 3)].dist = 1
                elif particle.NH_dict[dir_in_range(dir - 2)].type == "t":
                    particle.NH_dict[dir_in_range(dir - 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir + 1)].dist = 1
                    particle.NH_dict[dir_in_range(dir - 2)].dist = 0
                    #particle.NH_dict[dir_in_range(dir + 2)].dist = 2
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
                       # particle.NH_dict[dir_in_range(dir - 2)].dist = 2
                    elif particle.NH_dict[dir_in_range(dir - 1)].type == "t":
                        particle.NH_dict[dir_in_range(dir + 1)].dist = 0
                        particle.NH_dict[dir_in_range(dir - 1)].dist = 0
                        particle.NH_dict[dir_in_range(dir + 2)].dist = 1
                        #particle.NH_dict[dir_in_range(dir + 3)].dist = 2
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
                        #particle.NH_dict[dir_in_range(dir + 2)].dist = 2
                    elif particle.NH_dict[dir_in_range(dir + 1)].type == "t":
                        particle.NH_dict[dir_in_range(dir + 1)].dist = 0
                        particle.NH_dict[dir_in_range(dir - 1)].dist = 0
                        particle.NH_dict[dir_in_range(dir + 2)].dist = 1
                        #particle.NH_dict[dir_in_range(dir + 3)].dist = 2
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




def set_min_max_data(particle):
    for dir in particle.NH_dict:
        if particle.NH_dict[dir].type == "p":
            if particle.p_max_dist < particle.NH_dict[dir].dist:
                particle.p_max_dist = particle.NH_dict[dir].dist
                particle.p_dir = dir
                particle.p_hop = 1
        if particle.NH_dict[dir].type == "fl":
            if particle.NH_dict[dir].dist < particle.fl_min_dist:
                if particle.prev_dir != dir or particle.fl_cnt == 1:
                    particle.fl_min_dist = particle.NH_dict[dir].dist
                    particle.fl_dir = dir
                    particle.fl_hop = 1


def check_data_received(particle):
    if particle.read_whole_memory():
        particle.rcv_buf = particle.read_whole_memory()
        return True
    return False


def update_own_data_from_nh(particle):
    #if particle.own_dist == 10000:
    p_dist_dict = update_own_dist_from_nh(particle)
    if p_dist_dict:
        update_nh_dict(particle)
    else:
        pass
        """
        I did not received any new distance but I have my own distance.
        No I have to find out the neighborhood distance of my free markers.
        Look at the receiving buffer and find out the min distance. 
        If beside the sender particle are free marker give them distance
        + 1. 
        """
    comparing_fl_p_dist(particle)


def update_own_dist_from_nh(particle):
    p_dist_dict = {}
    for dir in particle.rcv_buf:
        if particle.rcv_buf[dir].own_dist != 10000:
            """
                  Take the distances of the neighborhood particles and store them in a list
            """
            p_dist_dict[dir] = particle.rcv_buf[dir].own_dist
            if particle.NH_dict[dir].type == "p":
                particle.NH_dict[dir].dist = particle.rcv_buf[dir].own_dist

    if p_dist_dict:
        if min(p_dist_dict.values()) + 1 < particle.own_dist:
            print(" P", particle.number, "changed its distance from", particle.own_dist, " to ",
                  min(p_dist_dict.values()) + 1)
            particle.own_dist = min(p_dist_dict.values()) + 1
        return p_dist_dict
    else:
        return False
        # Give yourself a distance if you are not beside a tile
        # particle.own_dist = min(p_dist_list, key=p_dist_list.get)+1


def update_nh_dict(particle):
    for dir in particle.rcv_buf:
        if particle.rcv_buf[dir].own_dist + 1 == particle.own_dist:
            if particle.NH_dict[dir_in_range(dir + 1)].type == "fl":
                particle.NH_dict[dir_in_range(dir + 1)].dist = particle.own_dist
                if particle.fl_dir is None:
                    particle.fl_min_dist = particle.own_dist
                    particle.fl_dir = dir_in_range(dir + 1)
                    particle.fl_hop = 1
            if particle.NH_dict[dir_in_range(dir - 1)].type == "fl":
                particle.NH_dict[dir_in_range(dir - 1)].dist = particle.own_dist
                if particle.fl_dir is None:
                    particle.fl_min_dist = particle.own_dist
                    particle.fl_dir = dir_in_range(dir - 1)
                    particle.fl_hop = 1

            # update = True
            # # if update == True:
            # #     #set_nh_dist(particle)
            # #     set_min_max_data(particle)


def comparing_fl_p_dist(particle):
    for dir in particle.rcv_buf:
        # only accept data for fl from particles that have a lower distance than you.
        find_min_fl(dir, particle)
        # Check for the for the particle that has the highest distance
        find_max_p(dir, particle)
    # if particle.p_max_dist == -1:
    #     particle.fl_dir = None


def find_min_fl(dir, particle):
    if particle.rcv_buf[dir].fl_min_dist < particle.fl_min_dist:  # got the sender a smaller fl?
        new_fl(dir, particle)
    # if the distances are the same
    elif particle.rcv_buf[dir].fl_min_dist == particle.fl_min_dist:
        # comparing hop_counts
        hop_compare(dir, particle)


def find_max_p(dir, particle):
    if particle.p_max_dist == -1 and particle.rcv_buf[dir].own_dist < particle.own_dist:
        particle.p_max_dist = particle.own_dist
        particle.p_dir = None
        particle.p_hop = 0
    if particle.rcv_buf[dir].own_dist != 10000 and particle.rcv_buf[dir].own_dist > particle.p_max_dist:
        particle.p_max_dist = particle.rcv_buf[dir].own_dist
        particle.p_dir = dir
        particle.p_hop = particle.rcv_buf[dir].p_hop + 1
    elif particle.rcv_buf[dir].p_max_dist > particle.p_max_dist:
        particle.p_max_dist = particle.rcv_buf[dir].p_max_dist
        particle.p_dir = dir
        particle.p_hop = particle.rcv_buf[dir].p_hop + 1
    elif particle.rcv_buf[dir].p_max_dist == particle.p_max_dist:
        if (particle.rcv_buf[dir].p_hop + 1) < particle.p_hop:
            particle.p_dir = dir
            particle.p_hop = particle.rcv_buf[dir].p_hop + 1


def new_fl(dir, particle):
    if particle.prev_dir != dir:
        particle.fl_min_dist = particle.rcv_buf[dir].fl_min_dist
        particle.fl_dir = dir
        particle.fl_hop = particle.rcv_buf[dir].fl_hop + 1


def hop_compare(dir, particle):
    if (particle.rcv_buf[dir].fl_hop + 1) < particle.fl_hop:
        new_fl(dir, particle)


def data_sending(particle):
    """
            4th round of the coating cylce:
            Each particle will share its information with its neighbors
            """
    package = info_package(particle.own_dist, particle.fl_min_dist, particle.fl_dir,
                           particle.fl_hop, particle.p_max_dist, particle.p_dir, particle.p_hop)
    for dir in direction:
        if particle.particle_in(dir):
            neighbor_p = particle.get_particle_in(dir)
            #invert the dir so the receiver particle knows from where direction it got the package
            particle.write_to_with(neighbor_p, key=invert_dir(dir), data=deepcopy(package))
            if debug:
                print("P", particle.number, "wrote to P", neighbor_p.number, "dir", dir_str(dir))
                print("Own distance ", particle.own_dist, "fl_min_dist =",
                      particle.fl_min_dist, "fl_dir =", dir_str(particle.fl_dir),
                      "fl_hop =", particle.fl_hop, "p_max_dist = ",
                      particle.p_max_dist,
                      "p_dir = ", dir_str(particle.p_dir), "p_hop =  ", particle.p_hop)


def moving_decision(particle, sim):
    """
            5th round of the coating cylce:
            Each particle will share its information with its neighbors
            I just move if there is a free marker thats distance is lower
            than a particles distance in the network.
            If I am beside a tile and get the information to move in a direction where
            there is no tile beside me I am not going to move.
    """
    if debug:
        print("\n", sim.get_actual_round())
    if particle.t_cnt > 3:
        #Optimization movementen between tiles
        if particle.t_cnt == 5:
            # data_clearing(particle)
            pass
        elif particle.t_cnt == 4:
            move_between_tiles(particle)

    else:
        if particle.fl_dir is not None:
            move_to_fl_dir(particle)
        # else:
        #     move_away_from_max(particle)
        # else:
    #     need_to_move(particle
    # )


def move_away_from_max(particle):
    for dir in particle.NH_dict:
        if particle.NH_dict[dir].type == "fl":
            if particle.NH_dict[dir].dist == particle.p_max_dist - 1:
                if not particle.particle_in(dir) and not particle.tile_in(dir):
                    moving(particle)
                    return

def move_to_fl_dir(particle):
    if not particle.particle_in(particle.fl_dir) and not particle.tile_in(particle.fl_dir):
        if particle.fl_dir != particle.prev_dir:
            if particle.p_max_dist != -1 and particle.own_dist < particle.p_max_dist:
                moving(particle)
                return True
            elif particle.fl_min_dist != 10000 and particle.own_dist > particle.fl_min_dist:
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
        # search for another free marker


def move_between_tiles(particle):
    for dir in direction:
        if particle.NH_dict[dir].type == "p" and particle.NH_dict[invert_dir(dir)].type == "fl":
            if invert_dir(dir) != particle.prev_dir :
                particle.fl_dir = invert_dir(dir)
                moving(particle)
                return
        elif particle.NH_dict[dir].type == "fl" and particle.NH_dict[invert_dir(dir + 3)].type == "fl":
            if dir != particle.prev_dir and not particle.particle_in(dir) and not particle.tile_in(dir):
                particle.fl_dir = dir
                moving(particle)
            elif not particle.particle_in(invert_dir(dir)) and not particle.tile_in(invert_dir(dir)):
                particle.fl_dir = invert_dir(dir)
                moving(particle)
            return



def check_for_fl(particle):
    # Move to the next fl that is equal or lower than your distance
    # only if there is a particle that has an higher distance than yours.
    for dir in particle.NH_dict:
        if particle.NH_dict[dir].type == "fl":
            if particle.p_max_dist > particle.own_dist:
                if (particle.NH_dict[dir].dist != 10000 or particle.NH_dict[dir].dist != -1) \
                        and particle.NH_dict[dir].dist <= particle.own_dist:
                    if particle.prev_dir != dir:
                        return dir
    return None



def moving(particle):
    if debug:
        print("\n P", particle.number, " coords before moving ", particle.coords)
    if particle.fl_dir is not None:
        particle.move_to(particle.fl_dir)
        particle.prev_dir = invert_dir(particle.fl_dir)
        if debug:
            print("\n P", particle.number, "moved to ", dir_str(particle.fl_dir), particle.fl_dir)
            print("\n P", particle.number, " coords after moving ", particle.coords)
        data_clearing(particle)
    else:
        if debug:
            print("\n P", particle.number, " could not move ")


def data_clearing(particle):
    particle.fl_dir = None
    particle.p_dir = None
    particle.wait = True