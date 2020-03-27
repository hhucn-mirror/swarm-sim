from copy import deepcopy

ONE_LAYER_COATING = False

ENTRANCE_LABEL = 3
PREVIOUS_LOCATION_LABEL = 10
BESIDE_PREVIOUS_LOCATION_LABEL = 5
FREE_LOCATION_LABEL = 1
FOUR_MATTERS = 4
FIVE_MATTERS = 5
TWO_MATTERS = 2
THREE_MATTERS = 3
CC_1 = PREVIOUS_LOCATION_LABEL + BESIDE_PREVIOUS_LOCATION_LABEL \
                    + ENTRANCE_LABEL + FREE_LOCATION_LABEL
CC_2 = PREVIOUS_LOCATION_LABEL + BESIDE_PREVIOUS_LOCATION_LABEL + 2 * FREE_LOCATION_LABEL
CC_3 = BESIDE_PREVIOUS_LOCATION_LABEL + ENTRANCE_LABEL \
                                                    + PREVIOUS_LOCATION_LABEL
CC_4 = PREVIOUS_LOCATION_LABEL + 2* FREE_LOCATION_LABEL



leader = None

def next_leader(world, uncoated_object, active_particles):
    global leader
    leader, distance, closest_tile_coordinates = get_leader_distance_to_object(world, uncoated_object, active_particles)
    leader.set_color((0.0, 1, 0.0, 1.0))
    setattr(leader, "directions_list", world.grid.get_directions_list())
    setattr(leader, "uncoated_locations", [])
    setattr(leader, "cave_uncoated_locations", [])
    setattr(leader, "path_uncoated_locations", [])
    setattr(leader, "uncoated_particles", active_particles.copy())
    if leader.coordinates in leader.uncoated_particles:
        if isinstance(leader.uncoated_particles, dict):
            del leader.uncoated_particles[leader.coordinates]
        else:
            leader.uncoated_particles.remove(leader.coordinates)
    leader.uncoated_particles = get_sorted_list_of_particles_distances(leader, leader.uncoated_particles)
    setattr(leader, "uncoated_object", [])
    setattr(leader, "aim", ())
    setattr(leader, "previous_location", leader.aim)
    setattr(leader, "aim_path", [])
    setattr(leader, "neighbors", {})
    setattr(leader, "obstacle_direction", False)
    setattr(leader, "cave_exit", [])
    setattr(leader, "dead_end_location", None)
    setattr(leader, "first_layer", True)
    setattr(leader, "state_storage", [])
    setattr(leader, "state", "toTile")
    if distance == 1:
        setattr(leader, "state", "scanning")
    else:
        setattr(leader, "state", "toTile")
        leader.aim = closest_tile_coordinates
        leader.aim_path = find_way_to_aim(leader.coordinates, closest_tile_coordinates, leader.world)
    return leader


def solution(world):
    global leader
    if world.get_actual_round() == 1:
        leader = next_leader(world, world.tile_map_coordinates, world.particle_map_coordinates)
    if leader:
        if leader.state == "toTile":
            handle_to_tile(leader)
        elif leader.state == "scanning":
            handle_scanning(leader)
        elif leader.state == "cave_scanning":
            handle_cave_scanning(leader)
        elif leader.state == "cave_discovery":
            handle_cave_discovery(leader)
        elif leader.state == "taking":
            handle_taking(leader)
        elif leader.state == "coating":
            handle_coating(leader)
        elif leader.state == "cave_escaping":
            handle_cave_escaping(leader)
        elif leader.state == "leader_coating":
            handle_leader_coating(leader)
        elif leader.state == "finished":
            handle_finished(leader)
            world.csv_round.update_finished()


def handle_scanning(leader):
    direction_entrance, direction_exit = checking_for_a_cave(leader)
    if direction_entrance and direction_exit:
        found_cave_entrance_go_for_cave_discovery(leader, direction_entrance, direction_exit)
    else:
        scanning(leader)
        if leader.coordinates in leader.uncoated_locations:
            finished_scanning(leader)


def found_cave_entrance_go_for_cave_discovery(leader, direction_entrance, direction_exit):
    cave_exit = leader.world.grid.get_coordinates_in_direction(leader.coordinates, direction_exit)
    leader.cave_exit.append(cave_exit)
    leader.state = "cave_discovery"
    leader.path_uncoated_locations.append(cave_exit)
    leader.path_uncoated_locations.append(leader.coordinates)
    leader.previous_location = leader.coordinates
    leader.move_to(direction_entrance)
    leader.world.csv_round.update_cave_discovery()


def scanning(leader):
    if leader.first_layer:
        direction = first_level_scanning(leader)
    elif leader.coordinates:
        direction = other_level_scanning(leader)
    if leader.coordinates not in leader.uncoated_locations and leader.coordinates not in leader.cave_uncoated_locations \
            and leader.coordinates not in leader.path_uncoated_locations :
        leader.uncoated_locations.append(leader.coordinates)
    leader.previous_location = leader.coordinates
    leader.move_to(direction)
    leader.world.csv_round.update_scanning()


def finished_scanning(leader):
    if leader.first_layer:
        leader.first_layer = False
    handle_scanned_locations(leader)
    if leader.uncoated_particles and leader.uncoated_locations:
        #go_taking_particles(leader)
        if not beaming(leader) and leader.uncoated_locations:
            it_is_leader_turn_to_coat(leader)
            #leader.state = "finished"
        else:
            leader.state="scanning"

    else:
        it_is_leader_turn_to_coat(leader)
    #leader.uncoated_locations = list(dict.fromkeys(leader.uncoated_locations))

def beaming(leader):
    leader.uncoated_locations = list(dict.fromkeys(leader.uncoated_locations))
    while leader.uncoated_locations:
        uncoated_location = leader.uncoated_locations.pop()
        if leader.coordinates==uncoated_location and leader.uncoated_particles:
            direction = obstacles_direction(leader)
            leader.move_to(direction)
        elif not leader.uncoated_particles:
            return False
            #handle_finished(leader)

        if leader.uncoated_particles:
            leader.take_particle_on(leader.uncoated_particles.pop())
            leader.drop_particle_on(uncoated_location)
            leader.uncoated_object.append(uncoated_location)
    if leader.uncoated_particles:
        #leader=next_leader(leader.world, leader.uncoated_object , leader.uncoated_particles)
        delete_cave_entrances(leader)
        leader.state="scanning"
        return True
    else:
        return False


def handle_scanned_locations(leader):
    if not ONE_LAYER_COATING:
        number_of_not_using_caves_locations = not_enough_particles(leader)
        if number_of_not_using_caves_locations:
            handle_not_enough_particles(leader, number_of_not_using_caves_locations)
        else:
            if leader.cave_uncoated_locations:
                leader.uncoated_locations.extend(leader.cave_uncoated_locations)
                leader.cave_uncoated_locations.clear()
    else:
        if leader.path_uncoated_locations:
            leader.uncoated_locations.extend(leader.path_uncoated_locations)
        if leader.cave_uncoated_locations:
            leader.uncoated_locations.extend(leader.cave_uncoated_locations)
            leader.cave_uncoated_locations.clear()
        leader.uncoated_locations = list(dict.fromkeys(leader.uncoated_locations))


def handle_not_enough_particles(leader, number_of_not_using_caves_locations):
    if leader.path_uncoated_locations:
        leader.uncoated_locations.extend(leader.path_uncoated_locations)
        if number_of_not_using_caves_locations != False and number_of_not_using_caves_locations != True \
                and leader.cave_uncoated_locations:
            for _ in range(1, number_of_not_using_caves_locations):
                leader.cave_uncoated_locations.pop(0)
            leader.uncoated_locations.extend(leader.cave_uncoated_locations)
    elif leader.cave_uncoated_locations:
        leader.uncoated_locations.extend(leader.cave_uncoated_locations)


def checking_for_a_cave(leader):
    get_neighbors(leader)
    if len(leader.neighbors) == FIVE_MATTERS:
        return None, None
    direction_entrance, direction_exit = check_cave_entrance(leader)
    return direction_entrance, direction_exit


def handle_cave_discovery(leader):
    if leader.coordinates not in leader.path_uncoated_locations:
        leader.path_uncoated_locations.append(leader.coordinates)
    get_neighbors(leader)
    if len(leader.neighbors) == FIVE_MATTERS:
        handling_dead_end(leader)
    else:
        if len(leader.neighbors) < FOUR_MATTERS:
            if len(leader.neighbors) == THREE_MATTERS:
                sum_of_neighbors_labels, neighbor_number_map_direction = label_neighbors(
                    leader)
                if sum_of_neighbors_labels == CC_4:
                    store_location_in_path_list(leader)
                else:
                    go_cave_scanning(leader)
            else:
                go_cave_scanning(leader)
        else:
            store_location_in_path_list(leader)

def store_location_in_path_list(leader):
    direction = obstacles_direction(leader)
    leader.previous_location = leader.coordinates
    leader.move_to(direction)


def go_cave_scanning(leader):
    leader.first_caving = True
    leader.state = "cave_scanning"


def handle_cave_scanning(leader):
    cave_scanning(leader)
    if leader.coordinates in leader.cave_uncoated_locations or leader.coordinates in leader.path_uncoated_locations:
        go_cave_escaping(leader)


def go_cave_escaping(leader):
    if leader.coordinates in leader.cave_uncoated_locations:
        leader.cave_uncoated_locations.remove(leader.coordinates)
        if leader.coordinates not in leader.path_uncoated_locations:
            leader.path_uncoated_locations.append(leader.coordinates)
    leader.aim = leader.cave_exit.pop()
    leader.aim_path = find_way_to_aim(leader.coordinates, leader.aim, leader.world)
    leader.state = "cave_escaping"


def cave_scanning(leader):
    get_neighbors(leader)
    direction_entrance, direction_exit = checking_for_a_cave(leader)
    if direction_entrance and direction_exit and not leader.first_caving:
        leader.state_storage.append("cave_scanning")
        found_cave_entrance_go_for_cave_discovery(leader, direction_entrance, direction_exit)
    else:
        leader.first_caving=False
        if len(leader.neighbors) == FIVE_MATTERS:
            direction = leader.world.grid.get_nearest_direction(leader.coordinates, leader.previous_location)
        elif get_an_adjacent_obstacle_directions(leader):
            direction = obstacles_direction(leader)
        if leader.coordinates not in leader.cave_uncoated_locations and leader.coordinates != leader.aim\
                and leader.coordinates not in leader.path_uncoated_locations:
            leader.cave_uncoated_locations.append(leader.coordinates)
        leader.previous_location = leader.coordinates
        leader.move_to(direction)
        leader.world.csv_round.update_cave_scanning()


def delete_cave_entrances(leader):
    if not ONE_LAYER_COATING:
        if leader.cave_exit and leader.cave_exit in leader.uncoated_locations:
            leader.uncoated_locations.remove(leader.cave_exit)
    leader.path_uncoated_locations.clear()
    leader.cave_uncoated_locations.clear()
    leader.cave_exit.clear()


def other_level_scanning(leader):
    direction = obstacles_direction(leader)
    return direction


def first_level_scanning(leader):
    if get_an_adjacent_obstacle_directions(leader, remove_particle=True):
        direction = obstacles_direction(leader)
    return direction


def check_cave_entrance(leader):
    sum_of_neighbors_labels, neighbor_number_map_direction = label_neighbors(
        leader)
    direction_entrance, direction_exit = get_cave_entry_and_exit( sum_of_neighbors_labels, neighbor_number_map_direction)

    return direction_entrance, direction_exit


def label_neighbors(leader):
    sum_of_neighbors_labels = 0
    neighbor_number_map_direction = {}
    for idx in range(len(leader.directions_list)):
        facing_direction = leader.directions_list[idx % len(leader.directions_list)]
        if leader.matter_in(facing_direction) is False:
            direction_left = leader.directions_list[(idx - 1) % len(leader.directions_list)]
            direction_right = leader.directions_list[(idx + 1) % len(leader.directions_list)]
            number = get_location_label(direction_left, direction_right, leader, facing_direction)
            sum_of_neighbors_labels += number
            neighbor_number_map_direction[number] = facing_direction
    return sum_of_neighbors_labels,  neighbor_number_map_direction


def get_location_label(direction_left, direction_right, leader, facing_direction):
    number = 0
    if leader.matter_in(direction_left) is True and leader.matter_in(direction_right) is True:
        number = ENTRANCE_LABEL

    elif leader.matter_in(direction_left) is True and  leader.matter_in(direction_right) is False\
            or leader.matter_in(direction_right) is True and  leader.matter_in(direction_left) is False:
        number = FREE_LOCATION_LABEL

    if leader.previous_location == leader.world.grid.get_coordinates_in_direction(leader.coordinates,
                                                                                  facing_direction):
        number = PREVIOUS_LOCATION_LABEL

    elif (leader.previous_location == leader.world.grid.get_coordinates_in_direction(leader.coordinates,
                                                                                     direction_left)
          and leader.matter_in(direction_left) is False) \
            or (leader.previous_location == leader.world.grid.get_coordinates_in_direction(leader.coordinates,
                                                                                           direction_right)
                and leader.matter_in(direction_right) is False):
        number = BESIDE_PREVIOUS_LOCATION_LABEL
    return number



def get_cave_entry_and_exit(sum_of_neighbors_labels, neighbor_number_map_direction):
    direction_entrance = None
    direction_exit = None
    if sum_of_neighbors_labels == CC_1:
        direction_entrance = neighbor_number_map_direction[ENTRANCE_LABEL]
        direction_exit = neighbor_number_map_direction[FREE_LOCATION_LABEL]
    elif sum_of_neighbors_labels == CC_2:
        direction_entrance = neighbor_number_map_direction[FREE_LOCATION_LABEL]
        direction_exit = neighbor_number_map_direction[BESIDE_PREVIOUS_LOCATION_LABEL]
    elif sum_of_neighbors_labels == CC_3:
        direction_entrance = neighbor_number_map_direction[ENTRANCE_LABEL]
        direction_exit = neighbor_number_map_direction[BESIDE_PREVIOUS_LOCATION_LABEL]
    if direction_entrance and direction_exit:
        return direction_entrance, direction_exit
    else:
        return None, None


def get_neighbors(leader):
    leader.neighbors = {}
    leader.obstacle_direction = None
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            leader.neighbors[dir] = leader.get_matter_in(dir)
            leader.obstacle_direction = dir


def adjacent_tile(leader):
    for dir in leader.directions_list:
        if leader.matter_in(dir) and leader.get_matter_in(dir).type=="tile":
            return True
    return False


def handling_dead_end(leader):
    leader.aim = leader.cave_exit.pop()
    leader.aim_path = find_way_to_aim(leader.coordinates, leader.aim, leader.world)
    if not adjacent_tile(leader):
        leader.dead_end_location = leader.coordinates
    if bool(leader.state_storage) == False:
        leader.cave_uncoated_locations.extend(leader.path_uncoated_locations)
        leader.path_uncoated_locations.clear()
    leader.state = "cave_escaping"


def handle_cave_escaping(leader):
    if reached_aim(leader.aim, leader):
        leader.previous_location = leader.coordinates
        leader.move_to(leader.world.grid.get_nearest_direction(leader.coordinates, leader.aim))
        if leader.state_storage:
            leader.state = leader.state_storage.pop()
        else:
            leader.state = "scanning"
        return


def handle_to_tile(leader):
    if reached_aim(leader.aim, leader):
        if leader.uncoated_particles:
            leader.state = "scanning"
        else:
            leader.state = "finished"
    else:
        leader.world.csv_round.update_to_tile()


def handle_taking(leader):
    if reached_aim(leader.aim, leader):
        go_coating(leader)
    else:
        leader.world.csv_round.update_taking()


def go_coating(leader):
    leader.take_particle_on(leader.aim)
    leader.aim = leader.uncoated_locations.pop()
    leader.aim_path = find_way_to_aim(leader.coordinates, leader.aim, leader.world)
    leader.state = "coating"


def handle_coating(leader):
    if reached_aim(leader.aim, leader):
        leader.drop_particle_on(leader.aim)
        get_neighbors(leader)
        if leader.uncoated_locations and leader.uncoated_particles:
            if ONE_LAYER_COATING and len(leader.uncoated_locations) == 1:
                it_is_leader_turn_to_coat(leader)
            else:
                go_taking_particles(leader)
        elif not leader.uncoated_locations and leader.uncoated_particles and not ONE_LAYER_COATING:
            go_scanning(leader)
        else:
            it_is_leader_turn_to_coat(leader)


def it_is_leader_turn_to_coat(leader):
    leader.state = "leader_coating"
    leader.aim = leader.uncoated_locations.pop()
    leader.aim_path = find_way_to_aim(leader.coordinates, leader.aim, leader.world)


def go_taking_particles(leader):
    leader.scanning = False
    leader.aim = leader.uncoated_particles.pop(0)
    leader.aim_path = find_way_to_aim(leader.coordinates, leader.aim, leader.world)
    leader.previous_location = leader.coordinates
    leader.state = "taking"


def not_enough_particles(leader):
    quantity_of_uncoated_particles = len(leader.uncoated_particles) + 1  # for the leader
    location_counter = len(leader.uncoated_locations)
    if leader.path_uncoated_locations:
        location_counter += len(leader.path_uncoated_locations)
    if leader.cave_uncoated_locations:
        location_counter += len(leader.cave_uncoated_locations)
    if quantity_of_uncoated_particles < location_counter:
        if quantity_of_uncoated_particles < location_counter:
            if quantity_of_uncoated_particles >= location_counter - len(leader.cave_uncoated_locations):
                return quantity_of_uncoated_particles - location_counter
            else:
                return True
    return False


def go_scanning(leader):
    leader.world.csv_round.update_layer()
    delete_cave_entrances(leader)
    leader.state = "scanning"


def handle_leader_coating(leader):
    if leader.coordinates == leader.aim:
        leader.state = "finished"
        leader.world.csv_round.update_leader_coating()
    elif reached_aim(leader.aim, leader):
        leader.state = "finished"
        leader.world.csv_round.update_leader_coating()
    else:
        leader.world.csv_round.update_leader_coating()
        # print("Finished")


def handle_finished(leader):
    particle_distance_list = []
    locations_distance_list = []
    for particle in leader.uncoated_particles:
        leader.world.particles.remove(leader.world.particle_map_coordinates[particle])
    if leader.world.particles:
        listi = leader.world.particles
    else:
        listi = leader.coated_particles
    for particle in listi:
        for direction in leader.world.grid.get_directions_list():
            if not particle.matter_in(direction):
                particle.create_location_in(direction)
        particle_distance_list.append(get_distance_to_closest_tile(particle.coordinates, leader.world))
    for location in leader.world.locations:
        locations_distance_list.append(get_distance_to_closest_tile(location.coordinates,leader.world))
    if particle_distance_list and locations_distance_list:
        check_valid_type(locations_distance_list, particle_distance_list, leader.world)


def check_valid_type(locations_distance_list, particle_distance_list, world):
    if max(particle_distance_list) <= min(locations_distance_list):
        leader.world.csv_round.update_valid(1)
        world.set_successful_end()
    else:
        leader.world.csv_round.update_valid(0)
        world.set_unsuccessful_end()


def get_sorted_list_of_particles_distances(leader, listi):
    distances = []
    tmp_dict = {}
    sorted_list_of_particles_coordinates = []
    for particle in listi:
        calculated_distance = leader.world.grid.get_distance(leader.coordinates, particle)
        distances.append(calculated_distance)
        tmp_dict[particle] = calculated_distance
    distances.sort()
    for distance in distances:
        for coords, dist in tmp_dict.items():
            if distance == dist and coords not in sorted_list_of_particles_coordinates:
                sorted_list_of_particles_coordinates.append(coords)
    return sorted_list_of_particles_coordinates


def get_sorted_list_of_locations_distances(leader, location_list):
    distances = []
    tmp_dict = {}
    sorted_list_of_locations_coordinates = []
    for location in location_list:
        distance = get_distance_to_closest_tile(location, leader.world)
        distances.append(distance)
        tmp_dict[location] = distance
    distances.sort(reverse=True)
    for distance in distances:
        for coords, dist in tmp_dict.items():
            if distance == dist and coords not in sorted_list_of_locations_coordinates:
                sorted_list_of_locations_coordinates.append(coords)
    return sorted_list_of_locations_coordinates


def obstacles_direction(leader):
    index_direction = leader.directions_list.index(leader.obstacle_direction)
    for idx in range(len(leader.directions_list)):
        direction = leader.directions_list[(idx + index_direction) % len(leader.directions_list)]
        if leader.matter_in(
                direction) is False and leader.previous_location == leader.world.grid.get_coordinates_in_direction(
                leader.coordinates, direction):
            idx_2 = len(leader.directions_list)
            while idx_2 >= 0:
                direction = leader.directions_list[(idx_2 + index_direction) % len(leader.directions_list)]
                if leader.matter_in(
                        direction) is False and leader.previous_location != leader.world.grid.get_coordinates_in_direction(
                    leader.coordinates, direction):
                    return direction
                idx_2 -= 1
        if leader.matter_in(
                direction) is False and leader.previous_location != leader.world.grid.get_coordinates_in_direction(
                leader.coordinates, direction):
            return direction
    return direction


def get_an_adjacent_obstacle_directions(leader, remove_particle=False):
    leader.obstacle_direction = None
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            if remove_particle and leader.get_matter_in(dir).type == "particle" \
                    and leader.get_matter_in(dir) in leader.uncoated_particles:
                leader.uncoated_particles.remove(leader.get_matter_in(dir))
            elif remove_particle and leader.matter_in(dir) and leader.get_matter_in(dir).type == "tile":
                leader.obstacle_direction = dir
                return True
            leader.obstacle_direction = dir
    if bool(leader.obstacle_direction):
        return True
    return False


def get_leader_distance_to_object(world, objact_list, am_list):
    closest_particle = None
    min = None
    for am_coordinates in am_list:
         for object_coordinates in objact_list:
            value = world.grid.get_distance(am_coordinates, object_coordinates)
            if min is None or (value < min):
                min = value
                if am_coordinates in world.particle_map_coordinates:
                    closest_particle = world.particle_map_coordinates[am_coordinates]
                closest_object_coordinate = object_coordinates
    return closest_particle, min, closest_object_coordinate

def find_way_to_aim(lcoordinates, tcoordinates, world):
    coord_lists = [[lcoordinates]]
    visited_coordinates = [lcoordinates]
    while len(coord_lists) > 0:
        current_list = coord_lists.pop(0)
        length = len(current_list)
        if are_aim_coordinates_reachable(tcoordinates, current_list[length - 1], world):
            if current_list[0] == lcoordinates:
                current_list.pop(0)
            current_list.append(tcoordinates)
            return current_list
        else:
            around_last = get_all_surounding_coordinates(current_list[length - 1], world)
            for tmp in around_last:
                if is_coord_unvisited_and_free(tmp, visited_coordinates, world):
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


def get_distance_to_closest_tile(source, world):
    distance = None
    for tile in world.get_tiles_list():
        value = world.grid.get_distance(source, tile.coordinates)
        if distance is None or (value < distance):
            distance = value
    return distance


def reached_aim(aim, leader):
    if leader.aim_path:
        get_neighbors(leader)
        next_direction = leader.world.grid.get_nearest_direction(leader.coordinates, leader.aim_path.pop(0))
        next_coords = leader.world.grid.get_coordinates_in_direction(leader.coordinates, next_direction)
        if aim == next_coords and leader.state != "leader_coating":
            return True
        leader.previous_location = leader.coordinates
        leader.move_to(next_direction)
        if leader.state == "leader_coating" and leader.coordinates == aim:
            return True
        return False
    return True