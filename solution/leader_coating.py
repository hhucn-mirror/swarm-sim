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
    directions_list = world.grid.get_directions_list()
    if world.get_actual_round() == 1:
        handle_first_round(directions_list, world)
        ##sim.get_particle_map_id()[leader]
    else:
        if leader.stage == "scanning":
            handle_scanning(leader)
        elif leader.stage == "taking":
            handle_taking(leader)
        elif leader.stage == "dropping":
            handle_dropping(leader)
        elif leader.stage == "checking":
            handle_checking(leader)


def handle_first_round(directions_list, world):
    global leader
    leader = getIdOfNearestParticleToIsland(world)
    leader.set_color((0.0, 1, 0.0, 1.0))
    setattr(leader, "get_an_obstacles_direction", get_an_obstacles_direction)
    setattr(leader, "directions_list", directions_list)
    setattr(leader, "move_around_obstacles", move_around_obstacles)
   # setattr(leader, "move_around_obstacles_anti", move_around_obstacles_anti)
    setattr(leader, "surroundings", [])
    setattr(leader, "coating_locations", [])
    setattr(leader, "starting_location", leader.coordinates)
    setattr(leader, "active_matters", world.particles.copy())
    leader.active_matters.remove(leader)
    setattr(leader, "obstacle_dir", leader.get_an_obstacles_direction(leader))
    leader.move_around_obstacles(leader)
    setattr(leader, "am_distances", get_sorted_list_of_particles_distances(leader))
    setattr(leader, "aim", ())
    setattr(leader, "prev_aim", leader.aim)
    setattr(leader, "aim_path", [])
    setattr(leader, "stage", "scanning")
    print("Start with scanning")


def reached_aim(aim, leader):
    if leader.aim_path:
        next_dir = leader.aim_path.pop(0)
        next_coords = header.get_coordinates_in_direction(leader.coordinates, next_dir)
        if header.get_coordinates_in_direction(leader.coordinates, next_dir) == leader.prev_aim:
            obstacle_dir = get_an_obstacles_direction(leader)
            if obstacle_dir:
                leader.aim_path = obstacle_avoidance(leader, obstacle_dir)
                next_dir = leader.aim_path.pop(0)
                next_coords = header.get_coordinates_in_direction(leader.coordinates, next_dir)
        if leader.tile_in(next_dir):
            leader.aim_path = obstacle_avoidance(leader, leader.directions_list.index(next_dir))
            return False
        if aim == next_coords:
            return True
        prev_aim = leader.coordinates
        if not leader.move_to(next_dir):
            print("obstacle")
            leader.aim_path = obstacle_avoidance(leader, leader.directions_list.index(next_dir))
            print ("new_path", leader.aim_path)
            return False
        leader.prev_aim = prev_aim
        #leader.move_to(next_dir)

        return False


def handle_scanning(leader):
    if leader.coordinates != leader.starting_location:
        leader.obstacle_dir = leader.get_an_obstacles_direction(leader)
        leader.move_around_obstacles(leader)
    else:
        if leader.am_distances:
            leader.aim = leader.am_distances.pop(0)
            leader.aim_path = leader.world.grid.get_shortest_path(leader.coordinates, leader.aim)

            leader.stage = "taking"
            print("from scanning --> taking")
        else:
            leader.stage = "leader"
            print("from scanning --> leader")


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
        leader.stage = "checking"
        print("from dropping -->  checking")


def handle_checking(leader):
    if not leader.coating_locations:
        print("from checking -->  scanning")
        leader.starting_location = leader.coordinates
        leader.obstacle_dir = leader.get_an_obstacles_direction(leader)
        leader.move_around_obstacles(leader)
        leader.stage = "scanning"
    elif not leader.am_distances:
        print("It is my turn")
        leader.stage = "leader"
    else:
        leader.aim = leader.am_distances.pop(0)
        leader.aim_path = leader.world.grid.get_shortest_path(leader.coordinates, leader.aim)
        leader.prev_aim = leader.coordinates
        print("from checking -->  taking")
        leader.stage = "taking"


# path = leader.world.grid.get_shortest_path(leader.coordinates, leader.aim)


def move_to_dest_in_one_rnd(particle, destiny):
    if move_to_dest_step_by_step(particle, destiny):
        return True
    move_to_dest_in_one_rnd(particle, destiny)


def move_to_dest_step_by_step(particle, destiny):
    next_dir = particle.world.grid.get_next_dir_to(particle.coordinates[0], particle.coordinates[1], destiny[0], destiny[1])
    next_coords = header.get_coordinates_in_direction(particle.coordinates, next_dir)
    if  next_coords == destiny:
        return True
    elif particle.matter_in(next_dir):
        next_dir = matter_avoidance(leader,leader.directions_list.index(next_dir))
    elif next_coords == leader.prev_aim:
        next_dir = matter_avoidance_anti(leader,leader.directions_list.index(next_dir))
        # print("Do not return back")
        # dir = get_an_obstacles_direction(leader)
        # next_dir = matter_avoidance(leader, dir)
        # next_coords = header.get_coordinates_in_direction(particle.coordinates, next_dir)
        # if next_coords == leader.prev_aim:
        #     while True:
        #         next_dir = random.choice(leader.directions_list)
        #         next_coords = header.get_coordinates_in_direction(particle.coordinates, next_dir)
        #         if next_coords != leader.prev_aim and leader.matter_in(next_dir) is False:
        #             break


    leader.prev_aim = leader.coordinates
    particle.move_to(next_dir)
    return False


def go_to_aim(aim_coords, leader):
    return move_to_dest_step_by_step(leader, aim_coords)


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


def obstacle_avoidance(leader, index_of_dir):
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
        path_1.extend( leader.world.grid.get_shortest_path(header.get_coordinates_in_direction(leader.coordinates, dir_1), leader.aim))
        path_2.extend(leader.world.grid.get_shortest_path(header.get_coordinates_in_direction(leader.coordinates, dir_2), leader.aim))
        if len(path_1) < len(path_2):
            if leader.prev_aim != header.get_coordinates_in_direction(leader.coordinates, dir_1):
                return path_1
        elif len(path_1) == len(path_2):
            if leader.prev_aim == header.get_coordinates_in_direction(leader.coordinates, dir_2):
                return path_1
        if leader.prev_aim == header.get_coordinates_in_direction(leader.coordinates, dir_2):
            return path_1
        return path_2

def matter_avoidance(leader, dir):
    if dir is not None:
        for idx in range(len(leader.directions_list)):
            dire = leader.directions_list[(idx + dir) % len(leader.directions_list)]
            if leader.matter_in(dire) is False:
                return dire
    return random.choice(leader.directions_list)

def matter_avoidance_anti(leader, dir):
    if dir is not None:
        idx = len(leader.directions_list)
        while idx >= 0:
            dire = leader.directions_list[(idx + dir) % len(leader.directions_list)]
            if leader.matter_in(dire) is False:
                return dire

def move_around_obstacles(leader):
    for idx in range(len(leader.directions_list)):
        dire = leader.directions_list[(idx + leader.obstacle_dir) % len(leader.directions_list)]
        if leader.matter_in(dire) is False:
            leader.move_to(dire)
            leader.coating_locations.append(leader.coordinates)
            break

def move_around_obstacles_anti(leader):
    idx = len(leader.directions_list)
    while idx >= 0 :
        dire = leader.directions_list[(idx + leader.obstacle_dir) % len(leader.directions_list)]
        if leader.matter_in(dire) is False:
            leader.move_to(dire)
            leader.coating_locations.append(leader.coordinates)
            break
        idx -= 1

def get_an_obstacles_direction(leader):
    for dir in leader.directions_list:
        if leader.matter_in(dir) is True:
            return leader.directions_list.index(dir)
    return False
    #return surroundings
# region surround island




def getIdOfNearestParticleToIsland(sim):
    closestParticle = sim.get_particle_list()[0]
    min = 1.7976931348623157e+308
    for particle in sim.get_particle_list():
        for tile in sim.get_tiles_list():
            xdiff = tile.coordinates[0] - particle.coordinates[0]
            ydiff = tile.coordinates[1] - particle.coordinates[1]
            value = math.sqrt((xdiff * xdiff) + (ydiff * ydiff))
            if (value < min):
                min = value
                closestParticle = particle
    return closestParticle
