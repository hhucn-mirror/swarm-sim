from copy import deepcopy


def solution(world):
    if world.get_actual_round() == 1:
        leaer = handle_first_round(world)
    else:
        if leader.state == "scanning":
            handle_scanning(leader)
        elif leader.state == "caving":
            handle_caving(leader)
        elif leader.state == "toTile":
            handle_to_tile(leader)
        elif leader.state == "taking":
            handle_taking(leader)
        elif leader.state == "dropping":
            handle_dropping(leader)
        elif leader.state == "get_out_from_cave":
            handle_get_out_from_cave(leader)
        elif leader.state == "checking":
            handle_checking(leader)
        elif leader.state == "self_positioning":
            handle_self_positioning(leader)


def handle_first_round(world):
    global leader
    leader, distance, closest_tile_coordinates = get_id_of_nearest_particle_to_island(world)
    leader.set_color((0.0, 1, 0.0, 1.0))
    setattr(leader, "directions_list", world.grid.get_directions_list())
    setattr(leader, "coating_locations", [])
    setattr(leader, "caving_locations", [])
    setattr(leader, "starting_location", ())
    setattr(leader, "active_matters", world.particles.copy())
    leader.active_matters.remove(leader)
    setattr(leader, "am_distances", get_sorted_list_of_particles_distances(leader))
    setattr(leader, "aim", ())
    setattr(leader, "prev_aim", leader.aim)
    setattr(leader, "aim_path", [])
    setattr(leader, "path_list", [])
    setattr(leader, "neighbors", {})
    setattr(leader, "obstacle_dir", False)
    setattr(leader, "cave_entrance", None)
    setattr(leader, "cave_exit", None)
    setattr(leader, "cave_coating", False)
    setattr(leader, "cave_found", False)
    setattr(leader, "first_level", True)
    setattr(leader, "level", 1)
    setattr(leader, "scanning", True)
    setattr(leader, "cave_1st_location", None)

    if distance == 1:
        leader.starting_location = leader.coordinates
        if get_an_adjacent_obstacle_directions_scanning(leader):
            dire = obstacles_free_direction(leader)
        leader.coating_locations.append(leader.coordinates)
        leader.prev_aim =  leader.coordinates
        leader.move_to(dire)
        setattr(leader, "state", "scanning")
        print("Start with scanning")
    else:
        setattr(leader, "state", "toTile")
        leader.aim = closest_tile_coordinates
        leader.aim_path = find_way_to_aim(leader.coordinates,  closest_tile_coordinates, leader.world)
        print("Start with going to Tile")
    return leader


def handle_scanning(leader):
    if leader.coordinates != leader.starting_location:
        dire, dire_exit = checking_for_a_cave(leader)
        if dire:
            leader.state = "caving"
            print("scanning --> caving")
        elif leader.first_level:
            dire = first_level_scanning(leader)
        else:
            dire = other_level_scanning(leader)
        leader.prev_aim = leader.coordinates
        leader.move_to(dire)
    else:
        leader.state = "checking"
        delete_cave_entrances(leader)
        if leader.first_level:
            print("1st_level_scanning --> checking")
            leader.first_level = False
            return
        print("scanning --> checking")


def checking_for_a_cave(leader):
    get_neighbors(leader)
    dir_entry, dir_exit = check_cave_entrance(leader)
    if dir_entry is not None and dir_exit is not None:
        handle_found_cave(leader, dir_entry, dir_exit)
    return dir_entry, dir_exit

def handle_found_cave(leader, dir_entry, dir_exit):
    leader.cave_found = True
    leader.cave_1st_location = leader.world.grid.get_coordinates_in_direction(leader.coordinates, dir_entry)
    leader.cave_entrance = leader.coordinates
    leader.cave_exit = leader.world.grid.get_coordinates_in_direction(leader.coordinates, dir_exit)
    if leader.cave_entrance in leader.coating_locations:
        leader.coating_locations.remove(leader.cave_entrance)
    if leader.cave_exit in leader.coating_locations:
        leader.coating_locations.remove(leader.cave_exit)
    if leader.cave_1st_location in leader.coating_locations:
        leader.coating_locations.remove(leader.cave_1st_location)
    if leader.level > 1:
        if leader.cave_exit not in leader.caving_locations:
            leader.caving_locations.append(leader.cave_exit)
        if leader.cave_entrance not in leader.caving_locations:
            leader.caving_locations.append(leader.cave_entrance)
        if leader.cave_1st_location not in leader.caving_locations:
            leader.caving_locations.append(leader.cave_1st_location)


def handle_caving(leader):
    get_neighbors(leader)
    if len(leader.neighbors) == 5:
        handle_tube_end(leader)
        return
    if get_an_adjacent_obstacle_directions_scanning(leader):
        dire = obstacles_free_direction(leader)
        # if get_an_adjacent_tile_directions_scanning(leader):
        if leader.coordinates not in leader.caving_locations\
                and leader.coordinates != leader.cave_exit\
                and leader.coordinates != leader.cave_entrance\
                and leader.coordinates != leader.cave_1st_location :
            leader.caving_locations.append(leader.coordinates)
            if leader.coordinates in leader.coating_locations:
                leader.coating_locations.remove(leader.coordinates)
        leader.prev_aim = leader.coordinates
        leader.move_to(dire)
    if leader.coordinates != leader.cave_exit\
                and leader.coordinates != leader.cave_entrance\
                and leader.coordinates != leader.cave_1st_location :
        return
    else:
        leader.aim=leader.cave_exit
        if leader.coordinates == leader.aim:
            print("from caving --> scanning")
            leader.state = "scanning"
            return
        leader.aim_path = find_way_to_aim(leader.coordinates, leader.aim, leader.world)
        print("from caving -->get out of the cave")
        leader.state = "get_out_from_cave"


def delete_cave_entrances(leader):
    if leader.cave_exit and leader.cave_exit in leader.coating_locations:
        leader.coating_locations.remove(leader.cave_exit)
    if leader.cave_1st_location and leader.cave_1st_location in leader.coating_locations:
        leader.coating_locations.remove(leader.cave_1st_location)
    if leader.cave_entrance and leader.cave_entrance in leader.coating_locations:
        leader.coating_locations.remove(leader.cave_entrance)


def other_level_scanning(leader):
    dire = obstacles_free_direction(leader)
    if leader.coordinates not in leader.coating_locations:
        leader.coating_locations.append(leader.coordinates)
    return dire


def first_level_scanning(leader):
    if get_an_adjacent_obstacle_directions_scanning(leader):
        dire = obstacles_free_direction(leader)
        if get_an_adjacent_tile_directions_scanning(leader) and leader.coordinates not in leader.coating_locations:
            leader.coating_locations.append(leader.coordinates)
    return dire


def check_cave_entrance(leader):
    location_cnt = 0
    sum_of_neighbors_numbers = 0
    neighbors = {}
    sum_of_neighbors_numbers, location_cnt = give_neighbors_numbers(sum_of_neighbors_numbers,
                                                                    leader, location_cnt, neighbors)
    dir_entry, dir_exit = encode_neighbors_numbers_to_get_cave_entry_and_exit(sum_of_neighbors_numbers,
                                                                          leader, location_cnt, neighbors)
    return dir_entry, dir_exit


def encode_neighbors_numbers_to_get_cave_entry_and_exit(sum_of_neighbors_numbers,  leader, location_cnt, neighbors):
    dir_entry = None
    dir_exit = None
    if location_cnt == 2:
        for dire in neighbors:
            if neighbors[dire] == 10:
                dir_exit = dire
            elif neighbors[dire] == 2:
                dir_entry = dire
    elif location_cnt == 3:
        for dire in neighbors:
            if neighbors[dire] == 2:
                dir_entry = dire
            elif neighbors[dire] == 5:
                dir_exit = dire
    elif location_cnt == 4 and sum_of_neighbors_numbers == 18:
        for dire in neighbors:
            if neighbors[dire] == 2:
                dir_entry = dire
            if neighbors[dire] == 1:
                dir_exit = dire
    elif location_cnt == 4 and sum_of_neighbors_numbers == 17:
        for dire in neighbors:
            if neighbors[dire] == 5:
                dir_exit = dire
            elif neighbors[dire] == 1:
                if leader.matter_in(dire) is False:
                    dir_entry = dire
    return dir_entry, dir_exit


def give_neighbors_numbers(sum_of_neighbors_numbers, leader, location_cnt, neighbors):
    for idx in range(len(leader.directions_list)):
        dire = leader.directions_list[(idx) % len(leader.directions_list)]
        if leader.matter_in(dire) is False:
            dire_left = leader.directions_list[(idx - 1) % len(leader.directions_list)]
            dire_right = leader.directions_list[(idx + 1) % len(leader.directions_list)]
            number = 0
            if leader.matter_in(dire_left) is True and leader.matter_in(dire_right) is True:
                number = 2
            elif leader.matter_in(dire_left) is True or leader.matter_in(dire_right) is True:
                number = 1
            if leader.prev_aim == leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire):
                number = 10
            elif (leader.prev_aim == leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire_left) \
                    and leader.matter_in(dire_left) is False)\
                or (leader.prev_aim == leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire_right) \
                    and leader.matter_in(dire_right) is False):
                number = 5
            sum_of_neighbors_numbers += number
            neighbors[dire] = number
            location_cnt += 1
    return sum_of_neighbors_numbers, location_cnt


def scan_adjacent_locations(leader):
    index_dir = leader.directions_list.index(leader.obstacle_dir)
    neighbors_string = ""
    for idx in range(len(leader.directions_list)):
        dire = leader.directions_list[(idx + index_dir) % len(leader.directions_list)]
        if leader.matter_in(dire) is True:
            neighbors_string = neighbors_string + "M"
        else:
            neighbors_string = neighbors_string + "L"
    return index_dir, neighbors_string


def get_neighbors(leader):
    leader.neighbors = {}
    leader.obstacle_dir = None
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            leader.neighbors[dir] = leader.get_matter_in(dir)
            leader.obstacle_dir = dir


def handle_tube_end(leader):
    leader.aim = leader.cave_exit
    leader.aim_path = find_way_to_aim(leader.coordinates, leader.aim, leader.world)
    if leader.coordinates not in leader.caving_locations:
        leader.caving_locations.append(leader.coordinates)
    print("from caving --> get out of the cave")
    leader.state = "get_out_from_cave"


def handle_get_out_from_cave(leader):
    if reached_aim(leader.aim, leader):
        leader.cave_coating = False
        leader.prev_aim = leader.coordinates
        leader.move_to(leader.world.grid.get_nearest_direction(leader.coordinates, leader.aim))
        if leader.scanning:
            print("from  get out of the cave --> scanning")
            leader.state = "scanning"
            return
        print("from  get out of the cave --> checking")
        leader.state = "checking"


def handle_to_tile(leader):
    if reached_aim(leader.aim, leader):
        leader.starting_location = leader.coordinates
        if get_an_adjacent_obstacle_directions(leader):
            dire = obstacles_free_direction(leader)
            leader.coating_locations.append(leader.coordinates)
            leader.prev_aim = leader.coordinates
            leader.move_to(dire)
        print("from toTile --> 1st level scanning")
        leader.state = "scanning"


def handle_taking(leader):
    if reached_aim(leader.aim, leader):
        leader.take_particle_on(leader.aim)
        if leader.caving_locations and leader.cave_coating:
            leader.aim = leader.caving_locations.pop()
            leader.aim_path = find_way_to_aim(leader.coordinates, leader.aim, leader.world)
        else:
            leader.cave_coating = False
            leader.aim = leader.coating_locations.pop()
            leader.aim_path = find_way_to_aim(leader.coordinates, leader.aim, leader.world)

        print("from taking --> dropping")
        leader.state = "dropping"


def handle_dropping(leader):
    if reached_aim(leader.aim, leader):
        leader.drop_particle_on(leader.aim)
        if leader.get_particle_in(leader.world.grid.get_nearest_direction(leader.coordinates, leader.aim)) in leader.active_matters:
            leader.active_matters.remove((leader.get_particle_in(leader.world.grid.get_nearest_direction(leader.coordinates, leader.aim))))
        if not leader.caving_locations and leader.cave_coating:
            leader.cave_coating = False
            leader.aim = leader.cave_exit
            leader.aim_path = find_way_to_aim(leader.coordinates, leader.aim, leader.world)
            leader.state = "get_out_from_cave"
            print("from dropping -->  to get out from cave")
            return
        get_neighbors(leader)
        dir, dir_exit = check_cave_entrance(leader)
        if dir and dir_exit and 3<=len(leader.neighbors) <5 and not leader.cave_found:
            handle_cave_entrance_while_dropping(dir, dir_exit, leader)

        leader.state = "checking"
        print("from dropping -->  checking")


def handle_cave_entrance_while_dropping(dir, dir_exit, leader):
    print("Im infront of cave")
    leader.cave_entrance = leader.coordinates
    leader.cave_1st_location =  leader.world.grid.get_coordinates_in_direction(leader.coordinates, dir)
    leader.cave_exit = leader.world.grid.get_coordinates_in_direction(leader.coordinates, dir_exit)
    if leader.cave_entrance in leader.coating_locations:
        leader.coating_locations.remove(leader.cave_entrance)
    if leader.cave_exit in leader.coating_locations:
        leader.coating_locations.remove(leader.cave_exit)
    if leader.cave_1st_location in leader.coating_locations:
        leader.coating_locations.remove(leader.cave_1st_location)


def handle_checking(leader):
    if not leader.coating_locations and not leader.caving_locations:
            print("from checking -->  scanning")
            leader.level += 1
            leader.starting_location = leader.coordinates
            if get_an_adjacent_obstacle_directions(leader):
                leader.scanning = True
                dire = obstacles_free_direction(leader)
                if leader.coordinates not in leader.coating_locations:
                    leader.coating_locations.append(leader.coordinates)
                leader.prev_aim = leader.coordinates
                leader.move_to(dire)
            if not leader.cave_coating:
                leader.cave_found = False
            leader.state = "scanning"
            return
    elif leader.caving_locations and not leader.cave_coating:
        print("active vs locations ", (len(leader.active_matters) + 1),
              len(leader.caving_locations))
        if (len(leader.active_matters) +1 ) < len(leader.caving_locations):
            if abs( len(leader.active_matters) + 1 - len(leader.caving_locations) ) == 1:
                inner_cave= leader.caving_locations[-1]
                outside_cave= leader.caving_locations[0]
                distance_inner = get_closest_tile_distance(inner_cave)
                distance_outside = get_closest_tile_distance(outside_cave)
                if distance_inner == distance_outside:
                    leader.caving_locations.pop(0)
                else:
                    leader.caving_locations.pop()
            else:
                leader.caving_locations.pop()

        leader.cave_coating = True

    print("from checking -->  fill_up_cave", leader.caving_locations)
    if leader.active_matters:
        print("from checking -->  taking")
        leader.scanning = False
        leader.am_distances = get_sorted_list_of_particles_distances(leader)
        leader.aim = leader.am_distances.pop(0)
        leader.aim_path = find_way_to_aim(leader.coordinates, leader.aim, leader.world)
        leader.prev_aim = leader.coordinates
        leader.state = "taking"
    else:
        print("It is my turn")
        leader.state = "self_positioning"
        if leader.cave_coating and leader.caving_locations:
            leader.aim = leader.caving_locations.pop()
        elif leader.coating_locations:
            leader.aim = leader.coating_locations.pop()
        if leader.coordinates == leader.aim:
            leader.state = "finished"
            print("Finished immediatly")
        leader.aim_path = find_way_to_aim(leader.coordinates, leader.aim, leader.world)


def handle_self_positioning(leader):
    if reached_aim(leader.aim, leader, True):
        leader.state = "finished"
        print("Finished")


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
            if distance == dist and coords not in sorted_list_of_particles_coordinates:
                sorted_list_of_particles_coordinates.append(coords)
    return sorted_list_of_particles_coordinates


def get_sorted_list_of_locations_distances(leader):
    distances =[]
    tmp_dict = {}
    sorted_list_of_locations_coordinates = []
    for location in leader.coating_locations:
        calculated_distance = leader.world.grid.get_distance(leader.coordinates, location)
        distances.append(calculated_distance)
        tmp_dict[location] = calculated_distance
    distances.sort()
    for distance in distances:
        for coords, dist in tmp_dict.items():
            if distance == dist and coords not in sorted_list_of_locations_coordinates:
                sorted_list_of_locations_coordinates.append(coords)
    return sorted_list_of_locations_coordinates


def obstacles_free_direction(leader):
    index_dir = leader.directions_list.index(leader.obstacle_dir)
    for idx in range(len(leader.directions_list)):
        dire = leader.directions_list[(idx + index_dir) % len(leader.directions_list)]
        if leader.matter_in(dire) is False and leader.prev_aim == leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire):
            idx_2 = len(leader.directions_list)
            while idx_2 >= 0:
                dire = leader.directions_list[(idx_2 + index_dir) % len(leader.directions_list)]
                if leader.matter_in(
                        dire) is False and leader.prev_aim != leader.world.grid.get_coordinates_in_direction(
                        leader.coordinates, dire):
                    return dire
                idx_2 -= 1
        if leader.matter_in(dire) is False and leader.prev_aim != leader.world.grid.get_coordinates_in_direction(
            leader.coordinates, dire):
            return dire
    return dire


def get_adjacent_obstacles_directions(leader):
    leader.obstacle_dir.clear()
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            leader.obstacle_dir.append(dir)
    if bool(leader.obstacle_dir):
        return True
    return False


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


def get_an_adjacent_tile_directions_scanning(leader):
    leader.obstacle_dir = None
    for dir in leader.directions_list:
        if leader.matter_in(dir) and leader.get_matter_in(dir).type == "tile":
            return True
    return False


def get_id_of_nearest_particle_to_island(world):
    closest_particle = world.get_particle_list()[0]
    min = None
    for particle in world.get_particle_list():
        for tile in world.get_tiles_list():
            value = world.grid.get_distance(particle.coordinates, tile.coordinates)
            if min is None or (value < min):
                min = value
                closest_particle = particle
                closest_tile_coordinate = tile.coordinates
    return closest_particle, min, closest_tile_coordinate


def find_way_to_aim(lcoordinates, tcoordinates, world):
    coord_lists = [[lcoordinates]]
    visited_coordinates = [lcoordinates]
    while len(coord_lists) > 0:
        current_list = coord_lists.pop(0)
        length = len(current_list)
        if are_aim_coordinates_reachable(tcoordinates, current_list[length - 1], world):
            if current_list[0] == leader.coordinates:
                current_list.pop(0)
            current_list.append(tcoordinates)
            return current_list
        else:
            around_last = get_all_surounding_coordinates(current_list[length - 1], world)
            for tmp in around_last:
                if (is_coord_unvisited_and_free(tmp, visited_coordinates, world)):
                    new_list = deepcopy(current_list)
                    new_list.append(tmp)
                    coord_lists.append(new_list)
                    visited_coordinates.append(tmp)


def are_aim_coordinates_reachable(acoordinates, bcoordinates, world):
    if acoordinates == bcoordinates:
        return True
    around = get_all_surounding_coordinates(acoordinates, world)
    for tmp in around:
        if tmp == bcoordinates:
            return True
    return False


def is_coord_unvisited_and_free(coord, visited_coordinates, world):
    if coord in visited_coordinates:
        return False
    if coord in world.get_particle_map_coordinates():
        return False
    if coord in world.get_tile_map_coordinates():
        return False
    return True


def get_all_surounding_coordinates(pcoordinates, world):
    surrounding_coordinates = []
    for direction in world.grid.get_directions_list():
        surrounding_coordinates.append(world.grid.get_coordinates_in_direction(pcoordinates, direction))
    return surrounding_coordinates

def get_closest_tile_distance(source):
    min = None
    for tile in leader.world.get_tiles_list():
        value = leader.world.grid.get_distance(source, tile.coordinates)
        if min is None or (value < min):
            min = value
    return min

def reached_aim(aim, leader, leader_positioning = False):
    if leader.aim_path:
        next_dir =  leader.world.grid.get_nearest_direction(leader.coordinates,  leader.aim_path.pop(0))
        next_coords = leader.world.grid.get_coordinates_in_direction(leader.coordinates, next_dir)
        if aim == next_coords and leader_positioning is False:
            return True
        leader.prev_aim = leader.coordinates 
        leader.move_to(next_dir)
        if leader_positioning and leader.coordinates == aim:
            return True
        return False
    return True