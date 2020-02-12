import logging
import math
import random
import sys
from copy import deepcopy
import lib.swarm_sim_header as header

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5
S = 6  # S for stop and not south

prev_dir = -1

def solution(world):
    global leader
    global cave_entrance_coordinates
    global cave_width
    global level
    if world.get_actual_round() == 1:
        handle_first_round(world)
        ##sim.get_particle_map_id()[leader]
    else:
        if leader.stage == "scanning":
            handle_scanning(leader)
        elif leader.stage == "toTile":
            handle_to_tile(leader)
        elif leader.stage == "taking":
            handle_taking(leader)
        elif leader.stage == "dropping":
            handle_dropping(leader)
        elif leader.stage == "checking":
            handle_checking(leader)


def handle_first_round(world):
    global leader
    leader, distance, closest_tile_coordinates = getIdOfNearestParticleToIsland(world)
    leader.set_color((0.0, 1, 0.0, 1.0))
    setattr(leader, "directions_list", world.grid.get_directions_list())
    setattr(leader, "coating_locations", [])
    setattr(leader, "starting_location", ())
    setattr(leader, "active_matters", world.particles.copy())
    leader.active_matters.remove(leader)
    setattr(leader, "am_distances", get_sorted_list_of_particles_distances(leader))
    setattr(leader, "aim", ())
    setattr(leader, "prev_aim", leader.aim)
    setattr(leader, "aim_path", [])
    setattr(leader, "obstacle_dir", False)
    if distance == 1:
        leader.starting_location = leader.coordinates
        if get_an_adjacent_obstacle_directions_scanning(leader):
            dire = obstacles_free_direction(leader)
        leader.coating_locations.append(leader.coordinates)
        leader.move_to(dire)
        setattr(leader, "stage", "scanning")
        print("Start with scanning")
    else:
        setattr(leader, "stage", "toTile")
        leader.aim = closest_tile_coordinates
        leader.aim_path = world.grid.get_shortest_path(leader.coordinates, closest_tile_coordinates)
        print("Start with going to Tile")



def handle_scanning(leader):
    if leader.coordinates != leader.starting_location:
        if get_an_adjacent_obstacle_directions_scanning(leader):
            dire = obstacles_free_direction(leader)
            leader.coating_locations.append(leader.coordinates)
            leader.prev_aim = leader.coordinates
            leader.move_to(dire)

    else:
        if leader.active_matters:
            leader.am_distances = get_sorted_list_of_particles_distances(leader)
            leader.aim = leader.am_distances.pop(0)
            leader.aim_path = leader.world.grid.get_shortest_path(leader.coordinates, leader.aim)

            leader.stage = "taking"
            print("from scanning --> taking")
        else:
            leader.stage = "leader"
            print("from scanning --> leader")

def handle_to_tile(leader):
    if reached_aim(leader.aim, leader):
        leader.starting_location = leader.coordinates
        if get_an_adjacent_obstacle_directions(leader):
            dire = obstacles_free_direction(leader)
            leader.coating_locations.append(leader.coordinates)
            leader.prev_aim = leader.coordinates
            leader.move_to(dire)

        print("from toTile --> scanning")
        leader.stage = "scanning"


def handle_taking(leader):
    if reached_aim(leader.aim, leader):
        leader.take_particle_on(leader.aim)
        leader.aim = leader.coating_locations.pop(0)
        leader.aim_path = leader.world.grid.get_shortest_path(leader.coordinates, leader.aim)
        print("from taking --> dropping")
        leader.stage = "dropping"


def handle_dropping(leader):
    if reached_aim(leader.aim, leader):
        leader.drop_particle_on(leader.aim)
        leader.active_matters.remove((leader.get_particle_in(leader.world.grid.get_nearest_direction(leader.coordinates, leader.aim))))
        leader.stage = "checking"
        print("from dropping -->  checking")


def handle_checking(leader):
    if not leader.coating_locations:
        print("from checking -->  scanning")
        leader.starting_location = leader.coordinates
        if get_an_adjacent_obstacle_directions(leader):
            dire = obstacles_free_direction(leader)
            leader.coating_locations.append(leader.coordinates)
            leader.move_to(dire)
        leader.stage = "scanning"
    elif leader.active_matters:
        leader.am_distances = get_sorted_list_of_particles_distances(leader)
        leader.aim = leader.am_distances.pop(0)
        leader.aim_path = leader.world.grid.get_shortest_path(leader.coordinates, leader.aim)
        leader.prev_aim = leader.coordinates
        print("from checking -->  taking")
        leader.stage = "taking"
    else:
        print("It is my turn")
        leader.stage = "leader"



def get_sorted_list_of_particles_distances(leader):
    distances =[]
    tmp_dict = {}
    sorted_list_of_particles_coordinates = []
    for particle in leader.active_matters:
        calculated_distance = leader.world.grid.get_distance(leader.coordinates, particle.coordinates)
        distances.append(calculated_distance)
        tmp_dict[particle.coordinates] = calculated_distance

    distances.sort()
    for distance in distances:
        for coords, dist in tmp_dict.items():
            if distance == dist:
                if coords not in sorted_list_of_particles_coordinates:
                    sorted_list_of_particles_coordinates.append(coords)
    return sorted_list_of_particles_coordinates


def obstacle_avoidance_path(leader, obstacle_dir):
    index_of_dir = leader.directions_list.index(obstacle_dir)
    if index_of_dir is not None:
        for idx in range(len(leader.directions_list)):
            dir_1 = leader.directions_list[(idx + index_of_dir) % len(leader.directions_list)]
            if leader.matter_in(dir_1) is False:
                break

        idx = len(leader.directions_list)
        while idx >= 0:
            dir_2 = leader.directions_list[(idx + index_of_dir) % len(leader.directions_list)]
            if leader.matter_in(dir_2) is False:
                break
            idx -= 1
        path_1 = [dir_1]
        path_2 = [dir_2]
        path_1.extend( leader.world.grid.get_shortest_path(leader.world.grid.get_coordinates_in_direction(leader.coordinates, dir_1), leader.aim))
        path_2.extend(leader.world.grid.get_shortest_path(leader.world.grid.get_coordinates_in_direction(leader.coordinates, dir_2), leader.aim))
        if len(path_1) < len(path_2):
            if leader.prev_aim != leader.world.grid.get_coordinates_in_direction(leader.coordinates, dir_1):
                return path_1
        elif len(path_1) == len(path_2):
            if leader.prev_aim == leader.world.grid.get_coordinates_in_direction(leader.coordinates, dir_2):
                return path_1
        if leader.prev_aim == leader.world.grid.get_coordinates_in_direction(leader.coordinates, dir_2):
            return path_1
        return path_2


def obstacles_free_direction(leader):
    index_dir = leader.directions_list.index(leader.obstacle_dir)
    for idx in range(len(leader.directions_list)):
        dire = leader.directions_list[(idx + index_dir) % len(leader.directions_list)]
        if leader.matter_in(dire) is False:
            return dire
            break


def get_adjacent_obstacles_directions(leader):
    leader.obstacle_dir.clear()
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            leader.obstacle_dir.append(dir)
    if bool(leader.obstacle_dir):
        return True
    return False
    #return surroundings
# region surround island


def get_an_adjacent_obstacle_directions(leader):
    leader.obstacle_dir = None
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            leader.obstacle_dir = dir
    if bool(leader.obstacle_dir):
        return True
    return False


def get_an_adjacent_obstacle_directions_scanning(leader):
    leader.obstacle_dir = None
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            if leader.get_matter_in(dir).type == "particle" and leader.get_matter_in(dir) in leader.active_matters:
                leader.active_matters.remove(leader.get_matter_in(dir))
            leader.obstacle_dir = dir
    if bool(leader.obstacle_dir):
        return True
    return False


def getIdOfNearestParticleToIsland(sim):
    closestParticle = sim.get_particle_list()[0]
    min = None
    for particle in sim.get_particle_list():
        for tile in sim.get_tiles_list():
            value = sim.grid.get_distance(particle.coordinates, tile.coordinates)
            if min is None:
                min = value
                closestParticle = particle
                closest_tile_coordinate = tile.coordinates
            elif (value < min):
                min = value
                closestParticle = particle
                closest_tile_coordinate = tile.coordinates
    return closestParticle, min, closest_tile_coordinate



def reached_aim(aim, leader):
    if leader.aim_path:
        next_dir = leader.aim_path.pop(0)
        next_coords = header.get_coordinates_in_direction(leader.coordinates, next_dir)
        print(" next coords ", next_coords, " path ", leader.aim_path )
        if aim == next_coords:
            return True
        if header.get_coordinates_in_direction(leader.coordinates, next_dir) == leader.prev_aim:
            if get_an_adjacent_obstacle_directions(leader):
                leader.aim_path = obstacle_avoidance_path(leader, leader.obstacle_dir)
                next_dir = leader.aim_path.pop(0)
                next_coords = leader.world.grid.get_coordinates_in_direction(leader.coordinates, next_dir)
        if leader.tile_in(next_dir):
            print(" tile obstacle ")
            leader.aim_path = obstacle_avoidance_path(leader, next_dir)
            print(" new path ", leader.aim_path)

            return False
        prev_aim = leader.coordinates
        if not leader.move_to(next_dir):
            print("obstacle")
            leader.aim_path = obstacle_avoidance_path(leader, next_dir)
            print ("new_path", leader.aim_path)
            return False
        leader.prev_aim = prev_aim
        #leader.move_to(next_dir)
        return False
